# (C) Copyright 2003 Nuxeo SARL <http://nuxeo.com>
# Author: Emmanuel Pietriga (ep@nuxeo.com)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
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

RSSChannel_meta_type = 'RSS Channel'

factory_type_information = (
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
    A workflow schema serves as a proxy for the CMF user to be able to
    crate new Workflow definitions without direct contact with the
    workflow tool.
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
        )
    
    title = ''
    description = ''
    channel_url = ''
    new_window = 0 #true if links to news items should open in new windows

    def __init__(self, id, channel_url = '', new_window = 0, **kw):
        self.id = id
        self.channel_url = channel_url
        self.new_window = new_window
        self._refresh_time = 0 # far in the past
##        self._text = ''
##        self._headers = {}
        self._data = {}
        
    #
    # API
    #

    security.declareProtected(ManagePortal, 'refresh')
    def refresh(self):
        """Refresh the channels from its source."""
        self._refresh()

    security.declareProtected(View, 'getData')
    def getData(self):
        """Get the data for this channel, as a dict."""

        #self._maybe_refresh()
        self._refresh()
        return self._data

    #
    # internal
    #

    def _maybe_refresh(self):
        """Refresh if on lazy refresh and the delay has elapsed."""

        if not self.lazy_refresh: # acquired from parent (portal_rss)
            LOG('RSSChannel refresh', DEBUG, 'not on lazy refresh')
            return
        delay = self.refresh_delay # acquired from parent (portal_rss)
        now = int(time.time())
        if now - self._refresh_time > delay:
            self._refresh()
        else:
            LOG('RSSChannel refresh', DEBUG, 'not refreshing (now=%s last=%s)' %
                (now, self._refresh_time))

    def _refresh(self):
        """Refresh the channels from its source."""
        
        LOG('RSSChannel refresh', DEBUG, 'refreshing from source')
        self._retrieveFeed()
        self._refresh_time = int(time.time())

    def _retrieveFeed(self):
        """Call URP which will fetch and parse the RSS/XML feed"""

        url = self.channel_url
        if not url.startswith('http://') or url.startswith('https://'):
            data = {'channel': {}, 'items': []}
        data = feedparser.parse(url)
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
                          }
        else:
            #even if it succeeds, there might still be no data in the feed
            #this happens when the parser finds out that the feed has not
            #changed since it was last retrieved
            if data.has_key('items') and data['items'] and data.has_key('channel') and data['channel'] :
                # Avoid modifying persistent object if nothing has changed.
                # data['items'] is empty if nothing has changed since the feed
                # was last retrieved
                
                #filter and reorganize data generated by URP
                items = []
                for it in data['items']:
                    item = {'title': '','url': ''}
                    #fill with actual values if exist (for robustness as this might
                    #depend on the quality of the feed)
                    if it.has_key('title'): item['title'] = it['title']
                    if it.has_key('link'): item['url'] = it['link']
                    items.append(item)
                filteredData = {'lines': items, 'newWindow': self.new_window}
                #init values
                filteredData['title'] = ''
                filteredData['description'] = ''
                filteredData['url'] = ''
                #fill with actual values if exist (for robustness as this might depend
                #on the quality of the feed)
                if (data.has_key('channel')):
                    chn=data['channel']
                    if (chn.has_key('title')):
                        filteredData['title']=chn['title']
                    if (chn.has_key('description')):
                        filteredData['description']=chn['description']
                    if (chn.has_key('link')):
                        filteredData['url']=chn['link']
                #assign data to object
                if self._data != filteredData:
                    self._data = filteredData
                    self.title = filteredData['title']
                    self.description = filteredData['description']

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
