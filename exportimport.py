# (C) Copyright 2006 Nuxeo SAS <http://nuxeo.com>
# Author:
# Dragos Ivan <div@nuxeo.com>
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
"""CPSRSS Tool XML Adapter.
"""

from zope.component import adapts
from zope.interface import implements
from zope.app import zapi

from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects
from Products.GenericSetup.utils import XMLAdapterBase
from Products.GenericSetup.utils import ObjectManagerHelpers
from Products.GenericSetup.utils import PropertyManagerHelpers

from Products.CMFCore.utils import getToolByName

from Products.GenericSetup.interfaces import INode
from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.interfaces import ISetupEnviron

from Products.CPSUtil.genericsetup import StrictTextElement
from Products.CPSUtil.genericsetup import getExactNodeText

from Products.CPSRSS.interfaces import IRSSTool
from Products.CPSRSS.interfaces import IRSSChannel

from Products.CPSRSS.RSSChannel import RSSChannel_meta_type
from Products.CPSRSS.RSSChannel import RSSChannel

TOOL = 'portal_rss'
NAME = 'rss'

def exportRSSTool(context):
    """Export RSS tool and subobjects as a set of XML files.
    """
    site = context.getSite()
    tool = getToolByName(site, TOOL, None)
    if tool is None:
        logger = context.getLogger(NAME)
        logger.info("Nothing to export.")
        return
    exportObjects(tool, '', context)

def importRSSTool(context):
    """Import RSS tool and subobjects from XML files.
    """
    site = context.getSite()
    tool = getToolByName(site, TOOL)
    importObjects(tool, '', context)


class RSSXMLAdapter(XMLAdapterBase, PropertyManagerHelpers):

    """XML im- and exporter for RSS feeds.
    """

    adapts(IRSSChannel, ISetupEnviron)
    implements(IBody)

    __used_for__ = IRSSChannel

    _LOGGER_ID = 'rss'

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractProperties())

        self._logger.info('%r rss feed exported.' % self.context.getId())
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgeProperties()

        self._initProperties(node)

        obj_id = str(node.getAttribute('name'))
        if not obj_id:
            # BBB: for CMF 1.5 profiles
            obj_id = str(node.getAttribute('id'))
        self._logger.info('%r rss feed imported.' % obj_id)


class RSSToolXMLAdapter(XMLAdapterBase, ObjectManagerHelpers,
                                  PropertyManagerHelpers):
    """XML importer and exporter for RSSTool.
    """

    adapts(IRSSTool, ISetupEnviron)
    implements(IBody)

    _LOGGER_ID = NAME
    name = NAME

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractProperties())
        node.appendChild(self._extractObjects())

        self._logger.info("RSS tool exported.")
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgeProperties()
            self._purgeObjects()

        self._initProperties(node)
        self._initObjects(node)

        self._logger.info("RSS tool imported.")

    def _initObjects(self, node):
        """Initialize subobjects from node children.
        """
        for child in node.childNodes:
            if child.nodeName != 'object':
                continue
            if child.hasAttribute('deprecated'):
                continue
            parent = self.context

            obj_id = str(child.getAttribute('name'))
            if obj_id not in parent.objectIds():
                meta_type = str(child.getAttribute('meta_type'))
                if meta_type != RSSChannel_meta_type:
                    raise ValueError(meta_type)
                ob = RSSChannel(obj_id)
                parent._setObject(obj_id, ob)
                
            if child.hasAttribute('insert-before'):
                insert_before = child.getAttribute('insert-before')
                if insert_before == '*':
                    parent.moveObjectsToTop(obj_id)
                else:
                    try:
                        position = parent.getObjectPosition(insert_before)
                        parent.moveObjectToPosition(obj_id, position)
                    except ValueError:
                        pass
            elif child.hasAttribute('insert-after'):
                insert_after = child.getAttribute('insert-after')
                if insert_after == '*':
                    parent.moveObjectsToBottom(obj_id)
                else:
                    try:
                        position = parent.getObjectPosition(insert_after)
                        parent.moveObjectToPosition(obj_id, position+1)
                    except ValueError:
                        pass

            obj = getattr(self.context, obj_id)
            importer = zapi.queryMultiAdapter((obj, self.environ), INode)
            if importer:
                importer.node = child

    def _extractObjects(self):
        fragment = self._doc.createDocumentFragment()
        items = self.context.objectItems()
        items.sort()
        for id, ob in items:
            exporter = zapi.queryMultiAdapter((ob, self.environ), INode)
            if not exporter:
                raise ValueError("RSS Feed %s cannot be adapted to INode" % ob)
            child = exporter._getObjectNode('object', False)
            fragment.appendChild(child)
        return fragment
