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
from plone.portlets.interfaces import IPortletDataProvider

from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ubify.policy import CyninMessageFactory as _
from ubify.policy.config import spacesdefaultaddablenonfolderishtypes

from Products.CMFCore.utils import getToolByName
from zope.app.component.hooks import getSite
from time import time


from statistics import getRecentlyActiveMembers
from ubify.policy.config import contentroot_details
from ubify.cyninv2theme import getLastChangeUID
from ubify.cyninv2theme import getLastChangeTimeElapsed

def _users_cachekey(method, self):
    """member and last item added based cache
    """
    membership = getToolByName(getSite(),'portal_membership')
    memberid = membership.getAuthenticatedMember()
    return hash((memberid, getLastChangeUID(self.request),getLastChangeTimeElapsed(self.request),self.context.getPhysicalPath()))


class IActivityPortlet(IPortletDataProvider):

    count = schema.Int(title=_(u'Number of items to display'),
                       description=_(u'How many items to list?'),
                       required=True,
                       default=10)


class Assignment(base.Assignment):
    implements(IActivityPortlet)

    def __init__(self, count=10):
        self.count = count

    @property
    def title(self):
        return _(u"Recently Active Users")

class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('activityportlet.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)
        self.context = aq_inner(self.context)
        self.portal = getSite()

    def render(self):
        return self._template()

    @property
    def available(self):
        return len(self._data())

    def recentactivemembersdata(self):
        return self._data()

    @ram.cache(_users_cachekey)
    def _data(self):
        try:
            #print "Calculating recent users... %s" % time()
            strpath = "/".join(self.context.getPhysicalPath())
            rootid = contentroot_details['id']
            objRoot = getattr(self.portal,rootid)
            if self.context == objRoot:
                strpath = "/".join(self.portal.getPhysicalPath())
            else:
                strpath = "/".join(self.context.getPhysicalPath())
        except AttributeError:
            strpath = "/".join(self.context.getPhysicalPath())
        return getRecentlyActiveMembers(self.context,strpath,self.data.count)

class AddForm(base.AddForm):
    form_fields = form.Fields(IActivityPortlet)
    label = _(u"Add Recently Active Users Portlet")
    description = _(u"A portlet that renders a tile list of recently active user's avatars within the context of the space and all contained spaces.")

    def create(self, data):
        return Assignment(count=data.get('count', 10))

class EditForm(base.EditForm):
    form_fields = form.Fields(IActivityPortlet)
    label = _(u"Edit Recently Active Users Portlet")
    description = _(u"A portlet that renders a tile list of recently active user's avatars within the context of the space and all contained spaces.")
