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

"""

import os, sys
from zLOG import LOG, INFO, DEBUG

from Products.CMFCore.DirectoryView import createDirectoryView

def cps_rss_i18n_update(self):
    """
    Importation of the po files for internationalization.
    """
    _log = []
    def pr(bla, _log=_log):
        if bla == 'flush':
            return '\n'.join(_log)
        _log.append(bla)
        if (bla):
            LOG('cps_i18n_update:', INFO, bla)

    def primp(pr=pr):
        pr(" !!! Cannot migrate that component !!!")

    def prok(pr=pr):
        pr(" Already correctly installed")

    portal = self.portal_url.getPortalObject()
    def portalhas(id, portal=portal):
        return id in portal.objectIds()

    pr(" Updating i18n support")


    Localizer = portal['Localizer']
    languages = Localizer.get_supported_languages()
    catalog_id = 'cpsrss'
    # Message Catalog
    if catalog_id in Localizer.objectIds():
        Localizer.manage_delObjects([catalog_id])
        pr(" Previous default MessageCatalog deleted for CPSRSS")

    # Adding the new message Catalog
    Localizer.manage_addProduct['Localizer'].manage_addMessageCatalog(
        id=catalog_id,
        title='CPSRSS messages',
        languages=languages,
        )

    cpsrssCatalog = Localizer.cpsrss

    # computing po files' system directory
    CPSRSS_path = sys.modules['Products.CPSRSS'].__path__[0]
    i18n_path = os.path.join(CPSRSS_path, 'i18n')
    pr("   po files are searched in %s" % i18n_path)
    pr("   po files for %s are expected" % str(languages))

    # loading po files
    for lang in languages:
        po_filename = lang + '.po'
        pr("   importing %s file" % po_filename)
        po_path = os.path.join(i18n_path, po_filename)
        try:
            po_file = open(po_path)
        except (IOError, NameError):
            pr("    %s file not found" % po_path)
        else:
            cpsrssCatalog.manage_import(lang, po_file)
            pr("    %s file imported" % po_path)

    # Translation Service Tool
    if portalhas('translation_service'):
        translation_service = portal.translation_service
        pr (" Translation Sevice Tool found in here ")
        try:
            if getattr(portal['translation_service'], 'cpsrss', None) == None:
                # translation domains
                translation_service.manage_addDomainInfo('RSSBox','Localizer/cpsrss')
                pr(" RSSBox domain set to Localizer/cpsrss")
        except:
            pass
    else:
        raise str('DependanceError'), 'translation_service'

    return pr('flush')

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
    ttool['RSS Box'].manage_changeProperties(title='portal_type_RSSBox_title',
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
            # Hack to Fix CMF 1.5 incompatibility
            if path.startswith("Products/"):
                path = path[len("Products/"):]
            createDirectoryView(portal.portal_skins, path, skin)
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

    ##############################################
    # i18n support
    ##############################################

    pr(cps_rss_i18n_update(self))
    
    pr("End of CPSRSS install")
    return pr('flush')
