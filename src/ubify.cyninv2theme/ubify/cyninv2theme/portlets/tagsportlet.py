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
from zope import schema
from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.memoize import ram
from plone.memoize import request
from plone.portlets.interfaces import IPortletDataProvider
from zope.app.component.hooks import getSite
from time import time

from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ubify.policy import CyninMessageFactory as _

from Products.CMFCore.utils import getToolByName
from statistics import getMostUsedTags
from ubify.cyninv2theme import getLastChangeUID
from ubify.cyninv2theme import getLastChangeTimeElapsed

class ITagsPortlet(IPortletDataProvider):

    count = schema.Int(title=_(u'Number of tags to display'),
                       description=_(u'How many tags to list?'),
                       required=True,
                       default=20)

class Assignment(base.Assignment):
    implements(ITagsPortlet)

    def __init__(self, count=20):
        self.count = count

    @property
    def title(self):
        return _(u"Tags Portlet")

def _tags_cachekey(method, self):
    """member and last item added based cache
    """
    membership = getToolByName(getSite(),'portal_membership')
    memberid = membership.getAuthenticatedMember()
    cachehash = hash((memberid, getLastChangeUID(self.request),getLastChangeTimeElapsed(self.request),self.context.getPhysicalPath()))
    return cachehash

class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('tagsportlet.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)
        self.context = aq_inner(self.context)
        self.portal = getSite()

    @property
    def available(self):
        return len(self._data())

    def render(self):
        return self._template()

    def mostusedtags(self):
        return self._data()

    @ram.cache(_tags_cachekey)
    def _data(self):
        #print "Calculating tags... %s" % time()
        strpath = "/".join(self.context.getPhysicalPath())
        results = getMostUsedTags(self.context,strpath,self.data.count)
        results.sort(lambda x,y: cmp(x['tagname'].lower(),y['tagname'].lower()),reverse=False)
        return results

class AddForm(base.AddForm):
    form_fields = form.Fields(ITagsPortlet)
    label = _(u"Add Tags Portlet")
    description = _(u"A portlet that renders a tag cloud of tags used within the context of the space and all contained spaces.")

    def create(self, data):
        return Assignment(count=data.get('count', 20))

class EditForm(base.EditForm):
    form_fields = form.Fields(ITagsPortlet)
    label = _(u"Edit Tags Portlet")
    description = _(u"A portlet that renders a tag cloud of tags used within the context of the space and all contained spaces.")
