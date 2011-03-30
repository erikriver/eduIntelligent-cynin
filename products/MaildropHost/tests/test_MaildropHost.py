#####################################################################
#
# test_MaildropHost unit tests for the MaildropHost object
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
#####################################################################
__version__ = "$Revision: 1405 $"[11:-2]

# Python imports
from unittest import TestCase, TestSuite, makeSuite, main

# Zope imports
import Testing
import Zope2
Zope2.startup()

# MaildropHost package imports
from Products.MaildropHost.MaildropHost import MaildropHost


class MaildropHostTests(TestCase):

    def setUp(self):
        mdh = MaildropHost('MDH', 'MDH Title')
        self.mdh = mdh

    def test_instantiation(self):
        self.assertEquals(self.mdh.getId(), 'MDH')
        self.assertEquals(self.mdh.title, 'MDH Title')
        self.assertEquals(self.mdh.isTransactional(), True)

    def test_edit(self):
        self.mdh.manage_makeChanges('New Title', transactional=False)
        self.assertEquals(self.mdh.title, 'New Title')
        self.assertEquals(self.mdh.isTransactional(), False)


def test_suite():
    return TestSuite((
        makeSuite( MaildropHostTests ),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
