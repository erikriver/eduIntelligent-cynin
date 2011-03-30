#####################################################################
#
# MaildropHost  An asynchronous MailHost replacement
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
#####################################################################
__version__ = "$Revision: 1159 $"[11:-2]


def manage_addMaildropHost(id, title='Maildrop Host', REQUEST=None):
    """ Add a Maildrop Host object to an ObjectManager. """


class MaildropHost:
    """

    MailHost objects work as asynchronous adapters to Simple Mail 
    Transfer Protocol (SMTP) servers.  MaildropHosts are used by 
    DTML 'sendmail' tags to find the proper host to deliver mail to.

    For the full API please see the MailHost API documentation in the
    Zope Help System. This file only lists those methods that differ
    from the standard MailHost API.

    """

    __constructor__=manage_addMaildropHost

    def manage_makeChanges(self, title, transactional=0, REQUEST=None, **kw):
        """ Edit the properties of a Maildrop Host """


    def isTransactional():
        """ Returns a truth value if run in transactional mode """
