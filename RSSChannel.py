# (C) Copyright 2003 Nuxeo SARL <http://nuxeo.com>
# Author: Emmanuel Pietriga (ep@nuxeo.com)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed 75in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id$
"""The RSS tool manages RSS channels and refreshes them.
"""

from zLOG import LOG, DEBUG

import time
import urllib
from StringIO import StringIO

from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo

from OFS.PropertyManager import PropertyManager
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.CMFCorePermissions import View
from Products.CMFCore.CMFCorePermissions import ModifyPortalContent
from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl

# (Ultraliberal RSS Parser) referred to as URP in this code
# http://diveintomark/projects/feed_parser/ultraliberal_rss_parser_20.html
# this parser is required for RSSChannel to function properly
# put feedreader.py in the same directory as RSSChannel.py
# or in your_zope_root/lib/python/
import feedparser

from sgmllib import SGMLParseError

RSSChannel_meta_type = 'RSS Channel'

factory_type_information =(
    {'id': 'RSS Channel',
     'description': 'RSS Channel',
     'title': '',
     'content_icon': 'document.gif',
     'product': 'RSSTool',
     'meta_type': RSSChannel_meta_type,
     'factory': 'addRSSChannel',
     'immediate_view': 'rsschannel_view',
     'filter_content_types': 0,
     'actions': ({'id': 'view',
                  'name': 'Voir',
                  'action': 'rsschannel_view',
                  'permissions': (View,),
                  'category': 'object',
                  },
                 {'id': 'edit',
                  'name': 'Modifier',
                  'action': 'rsschannel_edit_form',
                  'permissions': (ModifyPortalContent,),
                  'category': 'object',
                  },
                 ),
     },
    )



class RSSChannel(PortalContent, DefaultDublinCoreImpl):
    """
    RSSChannel handles calls to the RSS parser and reorganizes
    resulting data structures (mainly filtering)

    Restructuring gets rid of irrelevant data.
    """

    meta_type = RSSChannel_meta_type
    portal_type = RSSChannel_meta_type # to be able to add CMF object via ZMI

    security = ClassSecurityInfo()
    security.declareObjectProtected(View)

    _properties = (
        {'id':'title', 'type':'string', 'mode':'w', 'label':'Title'},
        {'id':'description', 'type':'text', 'mode':'w', 'label':'Description'},
        {'id':'channel_url', 'type':'string', 'mode':'w', 'label':'Channel URL'},
        {'id':'new_window', 'type':'boolean', 'mode':'w', 'label':'Open Links in New Window'},
        {'id':'nbMaxItems','type':'int', 'mode':'w', 'label': 'Maximum number of items'},
        {'id':'html_feed', 'type':'boolean', 'mode':'w',
         'label':'HTML feeds are provided untransformed'
         },
        )

    # filled by a refresh
    title = ''
    # filled by a refresh
    description = ''
    channel_url = ''
    #true if links to news items should open in new windows
    new_window = 1
    #maximum number of items, 0 means unlimited
    nbMaxItems = 0
    #true if the feed is already formatted in HTML,
    #in which case we provide it "as is" to the box
    html_feed = 0

    #remember last time we retrieved a feed so that we can manually
    #tell feedparser to go find it again or not (trying to correct
    #weird behaviour)
    _etag = None
    _modified = None

    def __init__(self, id, channel_url='', new_window=1, nbMaxItems=0,
                 html_feed=0, **kw):
        self.id = id
        self.channel_url = channel_url
        self.new_window = new_window
        self.nbMaxItems = nbMaxItems
        self.html_feed = html_feed
        self._refresh_time = 0 # far in the past
        self._data = {}

    #
    # API
    #

    security.declareProtected(ManagePortal, 'refresh')
    def refresh(self):
        """Refresh the channels from its source."""

        self._refresh()

    security.declareProtected(View, 'getData')

    def getData(self, maxItems=None):
        """Get the data for this channel, as a dict."""

        self._maybe_refresh()
        data = self._data.copy()
        lines = data['lines']
        maxItems = maxItems or self.nbMaxItems
        if maxItems:
            # O special case.
            # We want all the items
            data.update({'lines': lines[:maxItems]})
        return data

    #
    # internal
    #

    def _maybe_refresh(self):
        """Refresh if on lazy refresh and the delay has elapsed."""

        if not self.lazy_refresh: # acquired from parent (portal_rss)
            LOG('RSSChannel refresh', DEBUG, 'not on lazy refresh')
            self._refresh()
            return
        delay = self.refresh_delay # acquired from parent (portal_rss)
        now = int(time.time())
        if now - self._refresh_time > delay:
            LOG('RSSChannel refresh',DEBUG,' refreshing')
            self._refresh()
        else:
            LOG('RSSChannel refresh', DEBUG, 'not refreshing (now=%s last=%s)' %
                (now, self._refresh_time))

    def _refresh(self):
        """Refresh the channels from its source."""

        if self.html_feed:
            self._retrieveHTMLFeed()
        else:
            self._retrieveRSSFeed()
        self._refresh_time = int(time.time())

    def _retrieveRSSFeed(self):
        """Call URP which will fetch and parse the RSS/XML feed"""

        url = self.channel_url
        if not url.startswith('http://') or url.startswith('https://'):
            data = {'channel': {}, 'items': []}
        try :
            if (self._data.has_key('items') and self._data['items']):
                data = feedparser.parse(url,self._etag,self._modified)
            else:
                data = feedparser.parse(url,None,None)
        except SGMLParseError, err:
            data = {'channel': {}, 'items': []}
            LOG('RSSChannel Error', DEBUG,
                'RSS/SGML parsing error while retrieving feed\n'+str(url)+'\n'+str(err))
        if data.has_key('status') and data['status']>=400:
            #if the http request fails
            #the description field could contain more info about why
            #the request failed, like the error code (404, etc.)
            #but this might be overly complex/geeky in the general context
            self._data = {'title': "Broken RSS Channel",
                          'description': "URL " + url + " cannot be accessed.",
                          'url': url,
                          'lines': [],
                          'newWindow': self.new_window,
                          'feedType': 0, #RSS feed
                          }
        else:
            #even if it succeeds, there might still be no data in the feed
            #this happens when the parser finds out that the feed has not
            #changed since it was last retrieved
            if data['items'] and data['channel'] :
                # Avoid modifying persistent object if nothing has changed.
                # data['items'] is empty if nothing has changed since the feed
                # was last retrieved

                #filter and reorganize data generated by URP
                items = []
                for it in data['items']:
                    #fill with actual values if exist (for robustness
                    #as this might depend on the quality of the feed)
                    item = {}
                    if it.has_key('title') and it.has_key('link') \
                           and not (len(it['title'])==0 or it['title'].isspace()):
                        item['title'] = it['title']
                        item['url'] = it['link']
                        items.append(item)
                #if the max number of items to be displayed is limited
                #and the total number of items is higher, truncate
                if self.nbMaxItems and len(items) > self.nbMaxItems:
                    items = items[:self.nbMaxItems]
                #feedType=0 indicates an RSS feed
                filteredData = {'lines': items, 'newWindow': self.new_window, 'feedType': 0}
                #init values
                filteredData['title'] = ''
                filteredData['description'] = ''
                filteredData['url'] = ''
                #fill with actual values if exist (for robustness
                #as this might depend on the quality of the feed)
                if data.has_key('channel'):
                    chn=data['channel']
                    if (chn.has_key('title')):
                        filteredData['title']=chn['title']
                    if (chn.has_key('description')):
                        filteredData['description']=chn['description']
                    if (chn.has_key('link')):
                        filteredData['url']=chn['link']
                if data.has_key('etag'):
                    self._etag = data['etag']
                if data.has_key('modified'):
                    self._modified = data['modified']
                self.title = filteredData['title']
                if self.title is None or len(self.title)==0 or self.title.isspace():
                    self.title = self.id
                self.description = filteredData['description']
                #assign data to object
                if self._data != filteredData:
                    self._data = filteredData
            else:
                if not self._data.has_key('title') or \
                   len(self._data['title'])==0 or \
                   self._data['title'].isspace():
                    self._data['title'] = self.id
                if not self._data.has_key('description'):
                    self._data['description'] = ''
                if not self._data.has_key('url') or \
                   len(self._data['url'])==0 or \
                   self._data['url'].isspace():
                    self._data['url'] = url
                if not self._data.has_key('lines'):
                    self._data['lines'] = []
                if not self._data.has_key('newWindow'):
                    self._data['newWindow'] = self.new_window
                if not self._data.has_key('feedType'):
                    self._data['feedType'] = 0
                self.title = self._data['title']
                if self.title is None or len(self.title)==0 or self.title.isspace():
                    self.title = self.id
                self.description = self._data['description']
                if data.has_key('etag'):
                    self._etag = data['etag']
                if data.has_key('modified'):
                    self._modified = data['modified']

    def _retrieveHTMLFeed(self):
        """Fetch an HTML feed"""

        url = self.channel_url
        if not url.startswith('http://') or url.startswith('https://'):
            html_data = ''
        self.title = 'HTML Feed'
        self.description = "This feed has been formatted in HTML on the\
        server side. It can only be displayed as is ; no other information\
        is available."
        try:
            f = urllib.urlopen(url)
            html_data = f.read()
        except IOError:
            html_data = ''
            self.description = "An error occured while retrieving this feed"
        data = {'feedType':1, 'htmlData': html_data}
        if self._data != data:
            # Avoid modifying persistent object if nothing has changed.
            self._data = data

    #
    # ZMI
    #

    manage_options = (PropertyManager.manage_options +   # Properties
                      PortalContent.manage_options[:1] + # skip Edit
                      PortalContent.manage_options[3:]
                      )


InitializeClass(RSSChannel)


def addRSSChannel(container, id,
                  REQUEST=None, **kw):
    """Create an empty RSS Channel."""
    ob = RSSChannel(id, **kw)
    container._setObject(id, ob)
    ob = container._getOb(id)
    if REQUEST is not None:
        url = container.absolute_url()
        REQUEST.RESPONSE.redirect('%s/manage_main' % url)
