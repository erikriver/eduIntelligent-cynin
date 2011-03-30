#####################################################################
#
# MaildropHost Initialization
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
#####################################################################
__version__='$Revision: 1412 $'[11:-2]

from MaildropHost import addMaildropHostForm
from MaildropHost import MaildropHost
from MaildropHost import manage_addMaildropHost

def initialize( context ):
    try:
        context.registerClass( MaildropHost
                             , permission='Add MailHost objects'
                             , constructors=( addMaildropHostForm
                                            , manage_addMaildropHost
                                            )
                             , icon='www/maildrop.gif'
                            )

        context.registerHelp()
        context.registerHelpTitle('Maildrop Host')

    except:
        import traceback; traceback.print_exc()

