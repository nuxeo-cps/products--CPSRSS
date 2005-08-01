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
"""An RSS box displays an RSS channel in the portal.
"""

from zLOG import LOG, DEBUG
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CPSBoxes.BaseBox import BaseBox

factory_type_information = (
    {'id': 'RSS Box',
     'title': 'portal_type_RSSBox_title',
     'description': 'portal_type_RSSBox_description',
     'meta_type': 'RSS Box',
     'content_icon': 'box.png',
     'product': 'CPSRSS',
     'factory': 'addRSSBox',
     'immediate_view': 'rssbox_edit_form',
     'filter_content_types': 0,
     'actions': ({'id': 'view',
                  'name': 'View',
                  'action': 'basebox_view',
                  'permissions': (View,)},
                 {'id': 'edit',
                  'name': 'Edit',
                  'action': 'rssbox_edit_form',
                  'permissions': (ModifyPortalContent,)},
                 ),
     # additionnal cps stuff
     'cps_is_portalbox': 1,
     },
    )


class RSSBox(BaseBox):
    """An RSS Box (for displaying RSS channels)."""

    portal_type = meta_type = 'RSS Box'

    security = ClassSecurityInfo()

    _properties = BaseBox._properties + (
        {'id': 'channel_id', 'type': 'string', 'mode': 'w',
         'label': 'RSS Channel Id'},
        {'id': 'nbMaxItems', 'type': 'int', 'mode': 'w',
         'label': 'Maximum number of items'},
        )

    def __init__(self, id, channel_id='', nbMaxItems=0, **kw):
        BaseBox.__init__(self, id, provider='rss', category='rssbox', kw=kw)
        self.channel_id = channel_id
        self.nbMaxItems = nbMaxItems

InitializeClass(RSSBox)


def addRSSBox(dispatcher, id, REQUEST=None, **kw):
    """Add an RSS Box."""
    ob = RSSBox(id, **kw)
    dispatcher._setObject(id, ob)
    ob = getattr(dispatcher, id)
    ob.manage_permission(View, ('Anonymous',), 1)
    if REQUEST:
        url = dispatcher.DestinationURL()
        REQUEST.RESPONSE.redirect('%s/manage_main' % url)

