import unittest

#from zope.testing import doctestunit
#from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
ptc.setupPloneSite()

class ZipContentTestCase(ptc.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            import eduintelligent.zipcontent
            zcml.load_config('configure.zcml',
                             eduintelligent.zipcontent)
            ztc.installPackage('eduintelligent.zipcontent')
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass
    

def test_suite():
    return unittest.TestSuite([
        # Unit tests
        #doctestunit.DocFileSuite(
        #    'README.txt', package='eduintelligent.sco',
        #    setUp=testing.setUp, tearDown=testing.tearDown),

        #doctestunit.DocTestSuite(
        #    module='eduintelligent.sco.mymodule',
        #    setUp=testing.setUp, tearDown=testing.tearDown),


        # Integration tests that use PloneTestCase
        ztc.ZopeDocFileSuite(
            'README.txt', package='eduintelligent.zipcontent',
            test_class=ZipContentTestCase),

        #ztc.FunctionalDocFileSuite(
        #    'browser.txt', package='eduintelligent.sco',
        #    test_class=TestCase),
        
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')