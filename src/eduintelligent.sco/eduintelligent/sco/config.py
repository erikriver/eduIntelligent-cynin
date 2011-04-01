"""Common configuration constants
"""
import os
import Globals

PROJECTNAME = "eduintelligent.sco"

EXTERNAL_URL = "http://blufrog.iservices.com.mx/scorm"  # Use mod_rewrite for this
CONTENT_STORE = os.path.join(Globals.INSTANCE_HOME, 'var', 'eduintelligent')


