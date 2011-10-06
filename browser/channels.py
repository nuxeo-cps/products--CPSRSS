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

from copy import deepcopy
import logging
import operator

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import View
from Products.CPSonFive.browser import AqSafeBrowserView

from Products.CPSUtil.id import generateId

from Products.CPSRSS.RSSChannel import RSSChannel
from Products.CPSRSS.RSSChannelContainer import RSSChannelContainer
from Products.CPSRSS.RSSChannelContainer import addRSSChannelContainer

from Products.CPSRSS.interfaces import IRSSChannelContainer

from Products.CPSUtil.text import summarize

logger = logging.getLogger(__name__)

DEFAULT_RSS_ITEM_DISPLAY = 'cpsportlet_rssitem_display'

class ManageChannels(AqSafeBrowserView):
    """This view class serves as a view mostly for local channels.

    It does the container lookup, and provides interface to the container.
    It also maintains the list of channels to be rendered on context proxy,
    and provides the rendering logic.

    Some options make it possible for the regular portlet to call it as well,
    by forcing the container.
    This is still experimental, and will likely evolve in something
    more uniform, in which the portlet can also render local channels.
    """

    security = ClassSecurityInfo()

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

    def delChannels(self, chan_ids):
        chan_ids = self.request.form.get('chan_ids')
        if chan_ids is None:
            raise BadRequest("Missing channel ids to remove.")
        if isinstance(chan_ids, basestring):
            chan_ids = [chan_ids]
        cont = self.aqSafeGet('container')
        cont.manage_delObjects(chan_ids)
        self.redirectManageChannels()

    def channels(self, with_activation=True):
        cont = self.aqSafeGet('container')
        if cont is None:
            return ()
        proxy = self.context
        channels = cont.objectValues([RSSChannel.meta_type])
        if not with_activation:
            return channels

        dm = proxy.getContent().getDataModel(proxy=proxy)
        activated = dm.get('channels', ())
        return tuple(dict(channel=chan, activated=chan.getId() in activated)
                     for chan in channels)

    # traditional security declaration is necessary for browser:view,
    # and further in current Five 1.3.2 takes precedence over zcml
    # Actual protection must be declared, docstring created on the fly if
    # missing
    security.declareProtected(View, 'rssItems')
    def rssItems(self, cont_id=None, **kw):
        # straight adaptation from old skins script
        # now that proof-of-concept works, should be split
        if cont_id is None:
            cont = self.aqSafeGet('container')
        else:
            cont = self.context[cont_id]

        if cont is None:
            return ()

        logger.info("RSS channels from %r", cont)
        first_item = int(kw.get('first_item', 1))
        max_items = int(kw.get('max_items', 0))
        max_words = int(kw.get('max_words', 0))

        data_items = []
        channels_ids = kw.get('channels', [])
        for channel_id in channels_ids:
            if not cont.hasObject(channel_id):
                continue
            channel = cont[channel_id]
            if channel is None:
                continue
            data = channel.getData(max_items + first_item - 1)
            lines = deepcopy(data['lines']) # RSSChan did a simple copy
            for line in lines:
                # lines will be shuffled around (timely sort), so channel 
                # dependent display options have to be copied
                line['newWindow'] = data['newWindow']
            data_items += lines
            if first_item > 1:
                data_items = data_items[first_item - 1:]

        # If there is more than 1 channel we need to sort the rss items to
        # only keep the most recent ones, up to max_items.
        if len(channels_ids) > 1:
            # NOTE: One should replace "modified" with "updated" if switching
            # to a newer version of Feed Parser
            # http://feedparser.org/docs/date-parsing.html
            # Relying on the 'modified_parsed' item for the sorting.
            data_items.sort(key=operator.itemgetter('modified_parsed'),
                            reverse=True)
            data_items = data_items[:max_items]

        render_method = kw.get('render_method') or DEFAULT_RSS_ITEM_DISPLAY
        render_method = getattr(aq_inner(self.context), render_method, None)

        order = 0
        for item in data_items:
            description = item['description']
            modified = item['modified']
            author = item['author']
            if not author:
                author = 'unknown'

            # Item rendering and display
            rendered = ''

            # render the item using a custom display method (.zpt, .py, .dtml)
            if render_method is not None:
                item['summary'] = summarize(description, max_words)
                kw.update({'item': item,
                           'order': order,
                          })
                rendered = apply(render_method, (), kw)

            # this information is used by custom templates that call
            # getRSSItems() directly. GR TODO: who are these ?
            data_items[order].update(
                {'description': description,
                 'rendered': rendered,
                 'metadata':
                    {'creator': author,
                     'contributor': author,
                     'date': modified,
                     'issued': modified,
                     'created': modified,
                    },
                })
            order += 1

        return data_items

    def setActivated(self):
        """Set the list of activated channels."""
        activated = self.request.form.get('activated', ())
        proxy = self.context
        doc = proxy.getEditableContent()
        dm = doc.getDataModel(proxy=proxy)
        if not 'channels' in dm:
            raise RuntimeError(
                "Document type %r lacks fields for channels management",
                doc.portal_type)

        available = set(chan.getId()
                        for chan in self.channels(with_activation=False))
        dm['channels'] = [cid for cid in activated if cid in available]
        dm._commit()
        self.redirectManageChannels()

    def redirectManageChannels(self):
        self.request.RESPONSE.redirect('/'.join((
                self.context.absolute_url_path(), 'manage_channels.html')))

    def refresh(self):
        cont = self.aqSafeGet('container')
        if cont is not None:
            cont.refresh()
        self.redirectManageChannels()

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
        self.redirectManageChannels()

InitializeClass(ManageChannels)
