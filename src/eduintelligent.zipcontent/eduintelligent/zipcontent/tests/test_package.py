from unittest import defaultTestLoader

#from zope.testing import doctestunit
#from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import PloneSite

PloneTestCase.installProduct('eduintelligent.zipcontent')
PloneTestCase.setupPloneSite(products=['eduintelligent.zipcontent'])

class ZipContentTestCase(PloneTestCase.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            import eduintelligent.zipcontent
            zcml.load_config('configure.zcml',
                             eduintelligent.zipcontent)
            fiveconfigure.debug_mode = False
            #ptc.installPackage('eduintelligent.zipcontent')

        @classmethod
        def tearDown(cls):
            pass
    def test_create(self):
        
    #def test_installed(self):
        #quick_installer = self.portal.portal_quickinstaller 
        #portal_types = self.portal.portal_types
        
        #self.failUnless (quick_installer.isProductAvailable('eduintelligent.zipcontent'))
        #self.failUnless (quick_installer.isProductInstalled('eduintelligent.zipcontent'))
        #self.assertTrue('ZipContent' in portal_types.objectIds())
        
    

def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)
