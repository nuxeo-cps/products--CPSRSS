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
from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from OFS.Folder import Folder

from Products.CMFCore.permissions import View, ManagePortal
from Products.CMFCore.utils import UniqueObject

from RSSChannel import addRSSChannel, RSSChannel_meta_type

class RSSTool(UniqueObject, Folder):
    """RSS tool, a container for RSS channels that can refresh them."""

    id = 'portal_rss'
    meta_type = 'RSS Tool'

    security = ClassSecurityInfo()
    security.declareObjectProtected(View)

    #
    # API
    #
    security.declareProtected(ManagePortal, 'refresh')
    def refresh(self, REQUEST=None):
        """Refresh all the channels from their source."""
        for ob in self.objectValues(RSSChannel_meta_type):
            ob.refresh()
        if REQUEST:
            REQUEST.RESPONSE.redirect(
                '%s/manage_main?manage_tabs_message=Refreshed.'
                % self.absolute_url())

    #
    # CMF views
    #
    def __call__(self, REQUEST=None, **kw):
        """Default view."""
        return self.view(REQUEST=REQUEST, **kw)

    index_html = None  # This special value informs ZPublisher to use __call__

    security.declareProtected(View, 'view')
    def view(self, REQUEST=None, **kw):
        """Default view."""
        # FIXME rsstool_view doesn't exist
        return self.rsstool_view(REQUEST=REQUEST, **kw)

    #
    # ZMI
    #
    _properties = (
        {'id': 'title', 'type': 'string', 'mode': 'w', 
         'label': 'Title'},
        {'id': 'refresh_delay', 'type': 'int', 'mode': 'w', 
         'label': 'Refresh Delay'},
        {'id': 'lazy_refresh', 'type': 'boolean', 'mode': 'w', 
         'label': 'Lazy Refresh'},
    )
    title = ''
    refresh_delay = 1200 # 20 minutes
    lazy_refresh = 1

    all_meta_types = (
        {'name': RSSChannel_meta_type,
         'action': 'manage_addRSSChannelForm',
         'permission': ManagePortal,
         },
        )

    manage_addRSSChannelForm = DTMLFile('zmi/addRSSChannelForm', globals())

    security.declareProtected(ManagePortal, 'manage_addRSSChannel')
    def manage_addRSSChannel(self, id, channel_url, REQUEST=None, **kw):
        """Add a RSS Channel from the ZMI."""
        if REQUEST:
            kw.update(REQUEST.form)
            del kw['id']
        container = self
        addRSSChannel(container, id, channel_url)
        if REQUEST:
            REQUEST.RESPONSE.redirect('%s/%s/manage_workspace'
                                      % (container.absolute_url(), id))

    manage_options = (Folder.manage_options[:1] + # contents
                      ({'label': 'Refresh', 'action': 'refreshForm'},) +
                      Folder.manage_options[1:])

    refreshForm = DTMLFile('zmi/refreshForm', globals())


InitializeClass(RSSTool)
