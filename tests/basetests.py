# (C) Copyright 2006 Nuxeo SAS <http://nuxeo.com>
# Author: Dragos Ivan <div@nuxeo.com>
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

import os

from Testing.ZopeTestCase import ZopeTestCase

from Products.CPSDefault.tests.CPSTestCase import CPSTestCase
from Products.CPSDefault.tests.CPSTestCase import ExtensionProfileLayerClass

from Products.CPSRSS.RSSTool import RSSTool

def get_feed_url(feed_file):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), feed_file))


class LayerClass(ExtensionProfileLayerClass):
    extension_ids = ('CPSRSS:default',)

CPSRSSLayer = LayerClass(__name__, 'CPSRSSLayer')


class CPSRSSTestCase(CPSTestCase):
    """This class also tests that the profile does what it's supposed to."""
    layer = CPSRSSLayer

    def afterSetUp(self):
        self.tool = self.portal.portal_rss

class ZopeRSSTestCase(ZopeTestCase):

    def afterSetUp(self):
        self.folder._setObject('portal_rss', RSSTool())
        self.tool = self.folder.portal_rss

