# (C) Copyright 2003 Nuxeo SARL <http://nuxeo.com>
# Author: Emmanuel Pietriga <ep@nuxeo.com>
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

"""
CPSRSS Installer

HOWTO USE THAT ?

 - Log into the ZMI as manager
 - Go to your CPS root directory
* - Create an External Method with the following parameters:

     id    : CPSRSS Installer (or whatever)
     title : CPSRSS Installer (or whatever)
     Module Name   :  CPSRSS.install
     Function Name : install

 - save it
 - click now the test tab of this external method.
 - that's it !

"""

import os, sys
from zLOG import LOG, INFO, DEBUG


def install(self):
    """
    Starting point
    """
    _log = []
    def pr(bla, zlog=1, _log=_log):
        if bla == 'flush':
            return '<html><head><title>CPSRSS Installer</title></head><body><pre>'+ \
                   '\n'.join(_log) + \
                   '</pre></body></html>'

        _log.append(bla)
        if bla and zlog:
            LOG('CPSRSS Install:', INFO, bla)

    def prok(pr=pr):
        pr(" Already correctly installed")

    pr("Starting CPSRSS Install")

    portal = self.portal_url.getPortalObject()

    def portalhas(id, portal=portal):
        return id in portal.objectIds()

    ##########################################
    # TOOL
    ##########################################
    pr("Installing RSS Tool")
    if portalhas('portal_rss'):
        prok()
    else:
        pr(" Creating RSS Tool (portal_rss)")
        portal.manage_addProduct["CPSRSS"].manage_addTool('RSS Tool')

    ##########################################
    # PORTAL TYPE
    ##########################################

    pr("Installing Portal Types")

    ttool = portal.portal_types
    ptypes_installed = ttool.objectIds()
    
    if 'RSS Box' in ptypes_installed:
        pr(" Type RSS Box Deleted")
        ttool.manage_delObjects('RSS Box')
    pr(" Adding Type RSS Box")
    ttool.manage_addTypeInformation(id='RSS Box',
                                    add_meta_type='Factory-based Type Information',
                                    typeinfo_name='CPSRSS: RSS Box',)
    ttool['RSS Box'].manage_changeProperties(title='RSS Box',
                                             description='portal_type_RSSBox_description',
                                             content_meta_type='RSS Box')
                                    


    ##########################################
    # SKINS
    ##########################################

    pr("Installing Skins")

    skins = ('cps_rss',)
    paths = {'cps_rss': 'Products/CPSRSS/skins'}

    for skin in skins:
        path = paths[skin]
        path = path.replace('/', os.sep)
        pr(" FS Directory View '%s'" % skin)
        if skin in portal.portal_skins.objectIds():
            dv = portal.portal_skins[skin]
            oldpath = dv.getDirPath()
            if oldpath == path:
                prok()
            else:
                pr("  Correctly installed, correcting path")
                dv.manage_properties(dirpath=path)
        else:
            portal.portal_skins.manage_addProduct['CMFCore'].manage_addDirectoryView(\
                filepath=path, id=skin)
            pr("  Creating skin")
    allskins = portal.portal_skins.getSkinPaths()
    for skin_name, skin_path in allskins:
        if skin_name != 'Basic':
            continue
        path = [x.strip() for x in skin_path.split(',')]
        path = [x for x in path if x not in skins] # strip all
        if path and path[0] == 'custom':
            path = path[:1] + list(skins) + path[1:]
        else:
            path = list(skins) + path
        npath = ', '.join(path)
        portal.portal_skins.addSkinSelection(skin_name, npath)
        pr(" Fixup of skin %s" % skin_name)
    
    pr("End of CPSRSS install")
    return pr('flush')
