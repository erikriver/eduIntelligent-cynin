#####################################################################
#
# TransactionalMixin    Mixin classes for transactional behavior
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
#####################################################################
__version__ = "$Revision: 1312 $"[11:-2]

# NB: This implementation relies on the python GIL and the fact that a
#     transaction will only ever be touched from one thread.
#     IF EITHER OF THESE CHANGE, BE AFRAID!
import os

import transaction
transactions = {}

class TransactionalMixin:
    """ For Zope 2.8 and above
    """
    _transaction_done = False
    
    def _register(self):
        global transactions
        t = transaction.get()
        if transactions.has_key(t):
            et = transactions[t]
        else:
            et = EmailTransaction()
            t.join(et)
            transactions[t]=et
        et.register(self)

    def abort(self): 
        """ Called if the transaction has been aborted """
        try:
            os.remove(self._lockfile)
        except:
            pass

        try:
            os.remove(self._tempfile)
        except (IOError, OSError):
            pass

        self._tempfile = ''
        self._lockfile = ''

    def complete(self):
        """ Called when the transaction is okayed and the email can be sent """
        try:
            os.remove(self._lockfile)
        finally:
            self._lockfile = ''
            self._tempfile = ''
        
class SavePoint:
    """
    This does implement transaction.interfaces.ISavepointDataManager
    """

    next = None
    previous = None
    
    def __init__(self,et):
        self.et = et
        self.emails = []

    def append(self,email):
        self.emails.append(email)

    def _abort(self):
        for email in self.emails:
            email.abort()

    def abort(self):
        self._abort()
        if self.previous is not None:
            self.previous.abort()
        
    def complete(self):
        for email in self.emails:
            email.complete()
        if self.previous is not None:
            self.previous.complete()
            
    #######################################################
    # ZODB Transaction hooks
    #######################################################

    def rollback(self,set_et=True):
        """Rollback any work done since the savepoint.
        """
        self._abort()
        if set_et:
            self.et._savepoint = self
        else:
            self.previous=None
        if self.next is not None:
            self.next.rollback(False)
        self.next=None
            
class EmailTransaction:
    """
    This almost implements transaction.interfaces.IDataManager but doesn't have
    a transaction_manager attribute.
    """

    def __init__(self):
        self._savepoint = SavePoint(self)

    def register(self,email):
        self._savepoint.append(email)
        
    #######################################################
    # ZODB Transaction hooks
    #######################################################

    def abort(self, t):        
        """ Called if the transaction has been aborted """
        global transactions
        self._savepoint.abort()
        # NB: abort can get called more than once
        if transactions.has_key(t):
            # paranoia
            assert transactions[t] is self
            # transaction over
            del transactions[t]
        
    def tpc_begin(self, t): 
        """ Called at the beginning of a transaction """
        pass

    def commit(self, t): 
        """ Called for every (sub-)transaction commit """
        pass

    def tpc_vote(self, t):
        """ Only called for real transactions, not subtransactions """
        self._transaction_done = True

    def tpc_finish(self, t):
        """ Called at the end of a successful transaction """
        global transactions
        if self._transaction_done:
            self._savepoint.complete()
        # paranoia
        assert transactions[t] is self
        # transaction over
        del transactions[t]

    def tpc_abort(self, transaction): 
        """ Called on abort - but not always :( """
        pass

    def sortKey(self, *ignored):
        """ The sortKey method is used for recent ZODB compatibility which
            needs to have a known commit order for lock acquisition.
            I don't care about commit order, so return the constant 1
        """
        return 1

    def savepoint(self):
        """Return a data-manager savepoint (IDataManagerSavepoint).
        """
        old_sp = self._savepoint
        self._savepoint = SavePoint(self)
        old_sp.next = self._savepoint
        self._savepoint.previous = old_sp
        return self._savepoint

