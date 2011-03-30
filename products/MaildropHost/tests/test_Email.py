#####################################################################
#
# test_Email    unit tests for the Email and TransactionalEmail classes
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
#####################################################################
__version__ = "$Revision: 1618 $"[11:-2]

# Python imports
import os
from shutil import rmtree
from tempfile import mkdtemp
from unittest import TestCase
from unittest import TestSuite
from unittest import makeSuite
from unittest import main
import warnings

# Zope imports
import Testing
import transaction
import Zope2
Zope2.startup()

# MaildropHost imports
import Products.MaildropHost
from Products.MaildropHost.MaildropHost import Email
from Products.MaildropHost.MaildropHost import TransactionalEmail
from Products.MaildropHost.MaildropHost import _makeTempPath
from Products.MaildropHost.maildrop.stringparse import parse_assignments

BODY = 'This is a test message'
ADDRESS_SEQUENCE = [ '"Root" <root@localhost>\r\n'
                   , '"Postmaster" <postmaster@localhost>'
                   ]
ADDRESS_STRING = '"Root" <root@localhost>\r'
ADDRESS_USTRING = u'"Postmaster" <postmaster@localhost>\n'
NOMAIL = ('.', '..', '.svn', 'CVS')

config_path = os.path.join(Products.MaildropHost.__path__[0], 'config')
config = dict(parse_assignments(open(config_path).read()))
MAILDROP_SPOOL = config.get('MAILDROP_SPOOL', '')
if MAILDROP_SPOOL:
    MAILDROP_SPOOLS = [x.strip() for x in MAILDROP_SPOOL.split(';')]
else:
    MAILDROP_HOME = config['MAILDROP_HOME']
    MAILDROP_SPOOLS = [os.path.join(MAILDROP_HOME, 'spool')]
DEBUG_RECEIVER = config.get('DEBUG_RECEIVER', '')

def _listSpools():
    """ List all spool contents """
    files = []

    for spool in MAILDROP_SPOOLS:
        files.extend([x for x in os.listdir(spool) if x not in NOMAIL])

    return files


class EmailTestBase(TestCase):

    def setUp(self):
        # replace the spool setting from the config file with a temporary
        # spool directory
        self.original_spools = MAILDROP_SPOOLS[:]
        MAILDROP_SPOOLS[:] = [mkdtemp()]

    def temp_path(self):
        return _makeTempPath(MAILDROP_SPOOLS[0])

    def tearDown(self):
        # put the original spool setting back.
        rmtree(MAILDROP_SPOOLS[0])
        MAILDROP_SPOOLS[:] = self.original_spools

    def test_instantiation(self, klass):
        ae = self.assertEquals
        email1 = klass(ADDRESS_USTRING, ADDRESS_SEQUENCE, BODY, self.temp_path())

        if DEBUG_RECEIVER == '':
            ae(email1.m_to, '"Root" <root@localhost>,"Postmaster" <postmaster@localhost>')
        else:
            ae(email1.m_to, DEBUG_RECEIVER)
        ae(email1.m_from, u'"Postmaster" <postmaster@localhost>')
        ae(email1.body, BODY)

        email2 = klass(ADDRESS_STRING, ADDRESS_USTRING, BODY, self.temp_path())
        if DEBUG_RECEIVER == '':
            ae(email2.m_to, u'"Postmaster" <postmaster@localhost>')
        else:
            ae(email2.m_to, DEBUG_RECEIVER)
        ae(email2.m_from, '"Root" <root@localhost>')
        ae(email2.body, BODY)

        email3 = klass(ADDRESS_USTRING, ADDRESS_STRING, BODY, self.temp_path())
        if DEBUG_RECEIVER == '':
            ae(email3.m_to, '"Root" <root@localhost>')
        else:
            ae(email3.m_to, DEBUG_RECEIVER)
        ae(email3.m_from, u'"Postmaster" <postmaster@localhost>')
        ae(email3.body, BODY)


class EmailTests(EmailTestBase):

    def test_instantiation(self):
        EmailTestBase.test_instantiation(self, Email)

    def test_send(self):
        # Non-transactional emails write to the spool no matter what
        self.assertEquals(len(_listSpools()), 0)
        email1 = Email(ADDRESS_USTRING, ADDRESS_SEQUENCE, BODY, self.temp_path())
        email1.send()

        # Now that the email has been sent, there should only be the 
        # actual email file. The lockfile should be gone.
        self.assertEquals(len(_listSpools()), 1)

        # Make sure we clean up after ourselves...
        os.unlink(email1._tempfile)
        self.assertEquals(len(_listSpools()), 0)


class TransactionalEmailTests(EmailTestBase):

    def _makeAndSend(self):
        email = TransactionalEmail(ADDRESS_USTRING, ADDRESS_SEQUENCE, BODY,
                                   self.temp_path())
        email.send()
        return email


    def test_instantiation(self):
        EmailTestBase.test_instantiation(self, TransactionalEmail)


    def test_send_notransaction(self):
        # First of all, make sure we are in a clean transaction
        transaction.begin()

        # Transactional emails need a successful commit
        self.assertEquals(len(_listSpools()), 0)
        email1 = self._makeAndSend()
        email1_turd = email1._tempfile

        # Now that the email has been sent, there should be two files: The
        # lock file and the actual email. The lockfile stays until the
        # transaction commits.
        self.assertEquals(len(_listSpools()), 2)

        # Make sure we clean up after ourselves...
        os.unlink(email1_turd)
        os.unlink('%s.lck' % email1_turd)
        self.assertEquals(len(_listSpools()), 0)


    def test_send_transaction(self):
        # First of all, make sure we are in a clean transaction
        transaction.begin()

        self.assertEquals(len(_listSpools()), 0)
        email1 = self._makeAndSend()
        email1_turd = email1._tempfile

        # Now that the email has been sent, there should be two files: The
        # lock file and the actual email. The lockfile stays until the
        # transaction commits.
        self.assertEquals(len(_listSpools()), 2)

        # Committing the transaction will remove the lock file so that the
        # maildrop daemon will process the mail file. That means only the
        # mail file itself remains in the spool after the commit.
        transaction.commit()
        self.assertEquals(len(_listSpools()), 1)

        # Make sure we clean up after ourselves...
        os.unlink(email1_turd)
        self.assertEquals(len(_listSpools()), 0)

        # abort the current transaction
        transaction.abort()
        self.assertEquals(len(_listSpools()), 0)


    def test_send_subtransaction(self):
        from Products.MaildropHost.TransactionalMixin import transactions

        # First of all, make sure we are in a clean transaction
        transaction.begin()

        self.assertEquals(len(transactions.keys()), 0)
        self.assertEquals(len(_listSpools()), 0)
        email1 = self._makeAndSend()

        # Now that the email has been sent, there should be two files: The
        # lock file and the actual email. The lockfile stays until the
        # transaction commits.
        self.assertEquals(len(_listSpools()), 2)

        # Checking the transaction queue. A single transaction with a single
        # savepoint exists, which does not point to any other savepoints.
        self.assertEquals(len(transactions.keys()), 1)
        trans = transactions.values()[0]
        first_savepoint = trans._savepoint
        next = getattr(first_savepoint, 'next', None)
        previous = getattr(first_savepoint, 'previous', None)
        self.failUnless(next is None)
        self.failUnless(previous is None)

        # Committing a subtransaction should not do anything. Both email file
        # and lockfile should remain!
        transaction.savepoint(optimistic=True)
        self.assertEquals(len(_listSpools()), 2)

        # The transaction queue still contains a single transaction, but we 
        # now have two savepoints pointing to each other.
        self.assertEquals(len(transactions.keys()), 1)
        trans = transactions.values()[0]
        second_savepoint = trans._savepoint
        next = getattr(second_savepoint, 'next', None)
        previous = getattr(second_savepoint, 'previous', None)
        self.failUnless(next is None)
        self.failUnless(previous is first_savepoint)
        self.failUnless(previous.next is second_savepoint)

        # Send another email and commit the subtransaction. Only the spool
        # file count changes.
        email2 = self._makeAndSend()
        self.assertEquals(len(_listSpools()), 4)
        self.assertEquals(len(transactions.keys()), 1)
        transaction.savepoint(optimistic=True)
        self.assertEquals(len(_listSpools()), 4)

        # The transaction queue still contains a single transaction, but we 
        # now have three savepoints pointing to each other.
        self.assertEquals(len(transactions.keys()), 1)
        trans = transactions.values()[0]
        third_savepoint = trans._savepoint
        next = getattr(third_savepoint, 'next', None)
        previous = getattr(third_savepoint, 'previous', None)
        self.failUnless(next is None)
        self.failUnless(previous is second_savepoint)
        self.failUnless(previous.next is third_savepoint)

        # abort the current transaction, which will clean the spool as well
        # as the transactions mapping
        transaction.abort()
        self.assertEquals(len(_listSpools()), 0)
        self.assertEquals(len(transactions.keys()), 0)


    def test_send_subtransaction_oldstyle(self):
        from Products.MaildropHost.TransactionalMixin import transactions

        # Don't emit the DeprecationWarning we get
        warnings.filterwarnings('ignore', category=DeprecationWarning)

        # First of all, make sure we are in a clean transaction
        transaction.begin()

        self.assertEquals(len(transactions.keys()), 0)
        self.assertEquals(len(_listSpools()), 0)
        email1 = self._makeAndSend()

        # Now that the email has been sent, there should be two files: The
        # lock file and the actual email. The lockfile stays until the
        # transaction commits.
        self.assertEquals(len(_listSpools()), 2)

        # Checking the transaction queue. A single transaction with a single
        # savepoint exists, which does not point to any other savepoints.
        self.assertEquals(len(transactions.keys()), 1)
        trans = transactions.values()[0]
        first_savepoint = trans._savepoint
        next = getattr(first_savepoint, 'next', None)
        previous = getattr(first_savepoint, 'previous', None)
        self.failUnless(next is None)
        self.failUnless(previous is None)

        # Committing a subtransaction should not do anything. Both email file
        # and lockfile should remain!
        transaction.commit(1)
        self.assertEquals(len(_listSpools()), 2)

        # The transaction queue still contains a single transaction, but we 
        # now have two savepoints pointing to each other.
        self.assertEquals(len(transactions.keys()), 1)
        trans = transactions.values()[0]
        second_savepoint = trans._savepoint
        next = getattr(second_savepoint, 'next', None)
        previous = getattr(second_savepoint, 'previous', None)
        self.failUnless(next is None)
        self.failUnless(previous is first_savepoint)
        self.failUnless(previous.next is second_savepoint)

        # Send another email and commit the subtransaction. Only the spool
        # file count changes.
        email2 = self._makeAndSend()
        self.assertEquals(len(_listSpools()), 4)
        self.assertEquals(len(transactions.keys()), 1)
        transaction.commit(1)
        self.assertEquals(len(_listSpools()), 4)

        # The transaction queue still contains a single transaction, but we 
        # now have three savepoints pointing to each other.
        self.assertEquals(len(transactions.keys()), 1)
        trans = transactions.values()[0]
        third_savepoint = trans._savepoint
        next = getattr(third_savepoint, 'next', None)
        previous = getattr(third_savepoint, 'previous', None)
        self.failUnless(next is None)
        self.failUnless(previous is second_savepoint)
        self.failUnless(previous.next is third_savepoint)

        # abort the current transaction, which will clean the spool as well
        transaction.abort()
        self.assertEquals(len(_listSpools()), 0)
        self.assertEquals(len(transactions.keys()), 0)

        # Clean up warnfilter
        warnings.resetwarnings()


    def test_send_transaction_abort(self):
        # First of all, make sure we are in a clean transaction
        transaction.begin()

        self.assertEquals(len(_listSpools()), 0)
        email1 = self._makeAndSend()

        # Now that the email has been sent, there should be two files: The
        # lock file and the actual email. The lockfile stays until the
        # transaction commits.
        self.assertEquals(len(_listSpools()), 2)

        # Aborting a transaction should remove the email file and the
        # lockfile.
        transaction.abort()
        self.assertEquals(len(_listSpools()), 0)


    def test_savepoints(self):
        # First of all, make sure we are in a clean transaction
        transaction.begin()

        self.assertEquals(len(_listSpools()), 0)
        
        email1 = self._makeAndSend()
        
        # Now that the email has been sent, there should be two files: The
        # lock file and the actual email. The lockfile stays until the
        # transaction commits.        
        self.assertEquals(len(_listSpools()), 2)

        # create a savepoint
        savepoint1 = transaction.savepoint()

        # send a second mail
        email2 = self._makeAndSend()
        self.assertEquals(len(_listSpools()), 4)

        # create another savepoint
        savepoint2 = transaction.savepoint()
        
        # send a third mail
        email3 = self._makeAndSend()
        self.assertEquals(len(_listSpools()), 6)

        # rollback, this should remove email3
        savepoint2.rollback()        
        self.assertEquals(len(_listSpools()), 4)

        # rollback again, this should remove email2
        savepoint1.rollback()        
        self.assertEquals(len(_listSpools()), 2)
        
        # Aborting a transaction should remove the email file and the
        # lockfile.
        transaction.abort()
        self.assertEquals(len(_listSpools()), 0)


    def test_savepoints_earlier_rollback(self):
        from transaction.interfaces import InvalidSavepointRollbackError

        # First of all, make sure we are in a clean transaction
        transaction.begin()

        self.assertEquals(len(_listSpools()), 0)

        email1 = self._makeAndSend()
        
        # Now that the email has been sent, there should be two files: The
        # lock file and the actual email. The lockfile stays until the
        # transaction commits.
        self.assertEquals(len(_listSpools()), 2)

        # create a savepoint
        savepoint1 = transaction.savepoint()
        
        # send a second mail
        email2 = self._makeAndSend()
        self.assertEquals(len(_listSpools()), 4)

        # create another savepoint
        savepoint2 = transaction.savepoint()
        
        # send a third mail
        email3 = self._makeAndSend()
        self.assertEquals(len(_listSpools()), 6)

        # rollback should remove email2 and email3
        savepoint1.rollback()        
        self.assertEquals(len(_listSpools()), 2)

        # out of order rollback, should raise an exception
        self.assertRaises(InvalidSavepointRollbackError,
                          savepoint2.rollback)
        
        # Aborting a transaction should remove the email file and the
        # lockfile.
        transaction.abort()
        self.assertEquals(len(_listSpools()), 0)


    def test_savepoints_change_after_rollback(self):
        from transaction.interfaces import InvalidSavepointRollbackError

        # First of all, make sure we are in a clean transaction
        transaction.begin()

        self.assertEquals(len(_listSpools()), 0)

        email1 = self._makeAndSend()
        
        # Now that the email has been sent, there should be two files: The
        # lock file and the actual email. The lockfile stays until the
        # transaction commits.
        self.assertEquals(len(_listSpools()), 2)

        # create a savepoint
        savepoint1 = transaction.savepoint()
        
        # send a second mail
        email2 = self._makeAndSend()
        self.assertEquals(len(_listSpools()), 4)

        # rollback should remove email2
        savepoint1.rollback()        
        self.assertEquals(len(_listSpools()), 2)

        # send a third mail
        email3 = self._makeAndSend()
        self.assertEquals(len(_listSpools()), 4)

        # create another savepoint
        savepoint2 = transaction.savepoint()

        # rollback should remove email3
        savepoint1.rollback()        
        self.assertEquals(len(_listSpools()), 2)

        # out of order rollback, should raise an exception
        self.assertRaises(InvalidSavepointRollbackError,
                          savepoint2.rollback)
        
        # Aborting a transaction should remove the email file and the lockfile.
        transaction.abort()
        self.assertEquals(len(_listSpools()), 0)


def test_suite():
    return TestSuite((
        makeSuite(EmailTests),
        makeSuite(TransactionalEmailTests)
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
