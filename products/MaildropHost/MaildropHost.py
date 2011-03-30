#####################################################################
#
# MaildropHost  An asynchronous MailHost replacement
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
#####################################################################
__version__ = "$Revision: 1618 $"[11:-2]

# General python imports
from random import randint
from maildrop.stringparse import parse_assignments
from types import StringType
from types import UnicodeType
import os

# Zope imports
from Globals import DTMLFile
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from Products.MailHost.MailHost import MailHost

# MaildropHost package imports
from TransactionalMixin import TransactionalMixin


addMaildropHostForm=DTMLFile('dtml/add', globals())
def manage_addMaildropHost(self, id, title='Maildrop Host', REQUEST=None):
    """ add a MaildropHost into the system """
    mh = MaildropHost(id, title)
    self._setObject(id, mh)

    if REQUEST is not None:
        ret_url = '%s/%s/manage_main' % (self.absolute_url(), id)
        REQUEST['RESPONSE'].redirect(ret_url)


def _makeTempPath(spool_path):
    """ Compute safe temp path based on provided spool dir path """
    temp_path = os.path.join(spool_path, str(randint(100000, 9999999)))

    while os.path.exists(temp_path):
        temp_path = os.path.join(spool_path, str(randint(100000, 9999999)))

    return temp_path
    

class MaildropHost(MailHost):
    """ A MaildropHost """
    security = ClassSecurityInfo()
    meta_type = 'Maildrop Host'
    manage = manage_main = DTMLFile('dtml/edit', globals())
    manage_main._setName('manage_main')
    manage_log = DTMLFile('dtml/log', globals())

    manage_options = (
      ( { 'label' : 'Edit', 'action' : 'manage_main'
        , 'help' : ('MaildropHost', 'edit.stx')
        }
      , { 'label' : 'Maildrop Log', 'action' : 'manage_log'
        , 'help' : ('MaildropHost', 'log.stx')
        }
      )
      + MailHost.manage_options[1:]
      )

    def __init__(self, id='', title='Maildrop Host'):
        """ Initialize a new MaildropHost """
        self.id = id
        self.title = title
        self._transactional = True
        self._load_config()

    def _load_config(self):
        """ Read the config info and store as object attributes """
        import Products.MaildropHost
        default_config_path = os.path.join(Products.MaildropHost.__path__[0],
                                           'config')
        config_path = getattr(aq_base(self), 'config_path', default_config_path)
        config = dict(parse_assignments(open(config_path).read()))
        self.active_config_path = config_path
        self.smtp_host = config['SMTP_HOST']
        self.smtp_port = config['SMTP_PORT']
        self.debug = config['DEBUG'] and 'On' or 'Off'
        self._debug_receiver = config.get('DEBUG_RECEIVER', '') 
        self.debug_receiver =  self._debug_receiver or '(not set)'
        self.polling = config['MAILDROP_INTERVAL']
        MAILDROP_HOME = config['MAILDROP_HOME']
        MAILDROP_SPOOL = config.get('MAILDROP_SPOOL', '')
        if MAILDROP_SPOOL:
            MAILDROP_SPOOLS = [x.strip() for x in MAILDROP_SPOOL.split(';')]
        else:
            MAILDROP_SPOOLS = [os.path.join(MAILDROP_HOME, 'spool')]
        self.spool = MAILDROP_SPOOLS[0]

        for spool in MAILDROP_SPOOLS:
            if not os.path.isdir(spool):
                os.makedirs(spool)

        MAILDROP_TLS = config['MAILDROP_TLS']
        self.use_tls = ( (MAILDROP_TLS > 1 and 'Forced') or
                         (MAILDROP_TLS == 1 and 'Yes') or
                         'No' )
        self.login = config['MAILDROP_LOGIN'] or '(not set)'
        self.password = config['MAILDROP_PASSWORD'] and '******' or '(not set)'
        self.add_messageid = config.get('ADD_MESSAGEID', 0) and 'On' or 'Off'
        MAILDROP_LOG_FILE = config.get('MAILDROP_LOG_FILE')
        if not MAILDROP_LOG_FILE:
            MAILDROP_VAR = config.get('MAILDROP_VAR',
                                      os.path.join(MAILDROP_HOME, 'var'))
            MAILDROP_LOG_FILE = os.path.join(MAILDROP_VAR, 'maildrop.log')
        self.maildrop_log_file = MAILDROP_LOG_FILE

    def __setstate__(self, state):
        """ load the config when we're loaded from the database """
        MailHost.__setstate__(self, state)
        self._load_config()

    def _makeTempPath(self):
        """ Helper to create a temp file name safely """
        return _makeTempPath(self.spool)

    security.declareProtected('Change configuration', 'manage_makeChanges')
    def manage_makeChanges( self
                          , title
                          , transactional=False
                          , REQUEST=None
                          , **ignored
                          ):
        """ Change the MaildropHost properties """
        self.title = title
        self._transactional = not not transactional

        if REQUEST is not None:
            msg = 'MaildropHost "%s" updated' % self.id
            return self.manage_main(manage_tabs_message=msg)


    security.declareProtected('Change configuration', 'isTransactional')
    def isTransactional(self):
        """ Is transactional mode in use? """
        return getattr(self, '_transactional', True)


    def _send(self, m_from, m_to, body):
        """ Send a mail using the asynchronous maildrop handler """
        if self._debug_receiver != '':
            m_to = self._debug_receiver
        if self.isTransactional():
            email = TransactionalEmail(m_from, m_to, body,
                                       self._makeTempPath())
        else:
            email = Email(m_from, m_to, body, self._makeTempPath())

        return email.send()


    security.declareProtected('Change configuration', 'getLog')
    def getLog(self, max_bytes=50000):
        """ Return the maildrop daemon log contents, up to max_bytes bytes.

        If the file path is invalid, return an empty string
        """
        if not os.path.isfile(self.maildrop_log_file):
            return ''

        log_handle = open(self.maildrop_log_file, 'r')
        log_data = log_handle.read(max_bytes)
        log_handle.close()

        return log_data


class Email:
    """ Simple non-persistent class to model a email message """

    def __init__(self, mfrom, mto, body, temp_path):
        """ Instantiate a new email object """
        if not (isinstance(mto, StringType) or isinstance(mto, UnicodeType)):
            self.m_to = ','.join(mto).replace('\r', '').replace('\n', '')
        else:
            self.m_to = mto.replace('\r', '').replace('\n', '')
        self.m_from = mfrom.replace('\r', '').replace('\n', '')
        self.body = body
        self._tempfile = temp_path
        self._transactional = False


    def send(self):
        """ Write myself to the file system """
        temp_path = self._tempfile
        lock_path = '%s.lck' % temp_path

        lock = open(lock_path, 'w')
        lock.write('locked')
        lock.close()

        temp = open(temp_path, 'w')
        temp.write(MAIL_TEMPLATE % (self.m_to, self.m_from, self.body))
        temp.close()

        if not self._transactional:
            os.unlink(lock_path)
        else:
            self._lockfile = lock_path

        # At this point only the lockfile path is interesting, try
        # to save some memory by gutting the object
        self.m_to = self.m_from = self.body = ''


class TransactionalEmail(TransactionalMixin, Email):
    """ Transaction-aware email class """

    def __init__(self, mfrom, mto, body, temp_path):
        """ Instantiate a new transactional email object """
        Email.__init__(self, mfrom, mto, body, temp_path)
        self._lockfile = ''
        self._transaction_done = 0
        self._transactional = True
        self._register()


MAIL_TEMPLATE = """##To:%s
##From:%s
%s
"""


InitializeClass(MaildropHost) 

