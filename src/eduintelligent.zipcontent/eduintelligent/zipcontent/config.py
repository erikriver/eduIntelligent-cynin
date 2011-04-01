"""Common configuration constants
"""
import os
import Globals

PROJECTNAME = "eduintelligent.zipcontent"

EXTERNAL_URL = "http://blufrog.iservices.com.mx/scorm"  # Use mod_rewrite for this
#EXTERNAL_URL = "http://localhost/~erik/static"

#CONTENT_STORE = "/Users/erik/Sites/static"
CONTENT_STORE = os.path.join(Globals.INSTANCE_HOME, 'var', 'eduintelligent')
