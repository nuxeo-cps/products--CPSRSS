# -*- coding: iso-8859-15 -*-
# (C) Copyright 2002-2003 Nuxeo SARL <http://nuxeo.com>
# (C) Copyright 2002 Préfecture du Bas-Rhin, France
# Authors: Florent Guillaume <fg@nuxeo.com>
#          Emmanuel Pietriga <epietriga@nuxeo.com>
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

from Products.CMFCore.utils import ContentInit, ToolInit
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.permissions import AddPortalContent

import RSSTool
import RSSBox


contentClasses = (RSSBox.RSSBox,)
contentConstructors = (RSSBox.addRSSBox,)
fti = (RSSBox.factory_type_information + ())

registerDirectory('skins', globals())

tools = (RSSTool.RSSTool, )

def initialize(registrar):
    ContentInit('RSS Boxes',
                content_types=contentClasses,
                permission=AddPortalContent,
                extra_constructors=contentConstructors,
                fti=fti,
                ).initialize(registrar)
    ToolInit('RSS Tool',
             tools = tools,
             product_name = 'CPSRSS',
             icon = 'tool.gif',
             ).initialize(registrar)
