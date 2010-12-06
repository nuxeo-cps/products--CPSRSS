# (C) Copyright 2010 CPS-CMS Community <http://cps-cms.org/>
# Authors:
# G. Racinet <georges@racinet.fr>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from Products.CMFCore.utils import getToolByName
from Products.CPSonFive.browser import AqSafeBrowserView

from Products.CPSUtil.id import generateId

from Products.CPSRSS.RSSChannel import RSSChannel
from Products.CPSRSS.RSSChannelContainer import RSSChannelContainer
from Products.CPSRSS.RSSChannelContainer import addRSSChannelContainer

from Products.CPSRSS.interfaces import IRSSChannelContainer

class ManageChannels(AqSafeBrowserView):

    def __init__(self, *args, **kwargs):
        AqSafeBrowserView.__init__(self, *args, **kwargs)
        self.aqSafeSet('container', self.lookupContainer())

    def lookupContainer(self, cont_id=None):
        """Lookup the relevant container and set it up on self."""
        folder = self.context.aq_inner

        if cont_id is not None:
            try:
                cont = folder[cont_id]
            except KeyError:
                return None
            if not IRSSChannelContainer.providedBy(cont):
                return None

        # coding style that works if objectValues turns out to be a generator
        for cont in folder.objectValues([RSSChannelContainer.meta_type]):
            return cont

    def hasContainer(self):
        return self.aqSafeGet('container') is not None

    def channels(self):
        cont = self.aqSafeGet('container')
        if cont is None:
            return ()
        return cont.objectValues([RSSChannel.meta_type])

    def addChannel(self, url=None):
        """Create a channel from explicit url or from request form.

        All other properties are retrieved from the feed itself.
        """

        if url is None:
            # taking from request
            url = self.request.form['channel_url']

        cont = self.aqSafeGet('container')
        if cont is None:
            cont = addRSSChannelContainer(self.context)
            self.aqSafeSet('container', cont)
        channel = RSSChannel('channel', url).__of__(cont)
        d = channel.getData() # might be quite empty if feed has problems

        title = d.get('title', '')
        description = d.get('description', '')
        cid = generateId(title, container=cont)
        channel._setId(cid)
        channel.manage_changeProperties(title=title, description=description)

        cont._setObject(cid, channel)
        self.request.RESPONSE.redirect('/'.join((
                self.context.absolute_url_path(), 'manage_channels.html')))
