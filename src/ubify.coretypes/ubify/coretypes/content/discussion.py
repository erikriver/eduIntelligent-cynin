###############################################################################
#cyn.in is an open source Collaborative Knowledge Management Appliance that
#enables teams to seamlessly work together on files, documents and content in
#a secure central environment.
#
#cyn.in v2 an open source appliance is distributed under the GPL v3 license
#along with commercial support options.
#
#cyn.in is a Cynapse Invention.
#
#Copyright (C) 2008 Cynapse India Pvt. Ltd.
#
#This program is free software: you can redistribute it and/or modify it under
#the terms of the GNU General Public License as published by the Free Software
#Foundation, either version 3 of the License, or any later version and observe
#the Additional Terms applicable to this program and must display appropriate
#legal notices. In accordance with Section 7(b) of the GNU General Public
#License version 3, these Appropriate Legal Notices must retain the display of
#the "Powered by cyn.in" AND "A Cynapse Invention" logos. You should have
#received a copy of the detailed Additional Terms License with this program.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
#Public License for more details.
#
#You should have received a copy of the GNU General Public License along with
#this program.  If not, see <http://www.gnu.org/licenses/>.
#
#You can contact Cynapse at support@cynapse.com with any problems with cyn.in.
#For any queries regarding the licensing, please send your mails to
# legal@cynapse.com
#
#You can also contact Cynapse at:
#802, Building No. 1,
#Dheeraj Sagar, Malad(W)
#Mumbai-400064, India
###############################################################################
from Products.Archetypes.atapi import *
from Products.CMFCore.utils import getToolByName

from ubify.coretypes.config import PROJECTNAME
from Products.ATContentTypes.content.base import ATCTContent as BaseClass
from Products.ATContentTypes.content.schemata import ATContentTypeSchema

from zope.interface import implements
from ubify.coretypes.interfaces import IDiscussion
from plone.intelligenttext.transforms import convertWebIntelligentPlainTextToHtml,convertHtmlToWebIntelligentPlainText
from ubify.coretypes import generateDiscussionTitle
schema = ATContentTypeSchema.copy()

class Discussion(BaseClass):
    implements(IDiscussion)

    __doc__ = BaseClass.__doc__ + "(customizable version)"

    portal_type = 'Discussion'
    archetype_name = BaseClass.archetype_name

    if schema['title'] <> None and schema['title'].widget <> None:
        if schema['title'].required:
            schema['title'].required = False

    schema["title"].widget.visible = {"edit": "invisible", "view": "invisible"}

    if schema['description'] <> None and schema['description'].widget <> None:
        if not schema['description'].required:
            schema['description'].required = True
        if not schema['description'].primary:
            schema['description'].primary = True

    schema = schema

    def Title(self):
        if self.isTemporary():
            return None
        if self.title != '':
            return self.title;
        elif self.title == '' and self.getRawDescription() != '':
            return generateDiscussionTitle(convertWebIntelligentPlainTextToHtml(self.getRawDescription()))
        else:
            return None
    def Description(self):
        return convertWebIntelligentPlainTextToHtml(self.getRawDescription())

registerType(Discussion, PROJECTNAME)
