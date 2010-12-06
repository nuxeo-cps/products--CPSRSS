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

from Products.CMFCore.utils import ToolInit

import RSSTool

from Products.GenericSetup import profile_registry
from Products.GenericSetup import EXTENSION

from Products.CPSCore.interfaces import ICPSSite

tools = (RSSTool.RSSTool, )

def initialize(registrar):
    ToolInit('RSS Tool',
             tools = tools,
             icon = 'tool.png',
             ).initialize(registrar)
    profile_registry.registerProfile(
        'default',
        'CPS RSS',
        "RSS product for CPS.",
        'profiles/default',
        'CPSRSS',
        EXTENSION,
        for_=ICPSSite)
