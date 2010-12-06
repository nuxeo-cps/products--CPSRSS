# (C) Copyright 2010 CPS-CMS Community <http://cps-cms.org/>
# Authors:
# G. Racinet <georges@racinet.fr>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest

from basetests import ZopeRSSTestCase
from basetests import get_feed_url

from Products.CPSRSS.browser.channels import ManageChannels
from Products.CPSRSS.RSSChannelContainer import addRSSChannelContainer
from Products.CPSRSS.RSSTool import RSSTool


class FakeUrlTool(object):
    """Needed by generateID."""

    def __init__(self, portal=None):
        self.portal = portal

    def getPortalObject(self):
        return self.portal


class ManageChannelsTestCase(ZopeRSSTestCase):

    def afterSetUp(self):
        self.folder.portal_url = FakeUrlTool(portal=self.folder)
        self.folder.portal_rss = RSSTool()

    def makeView(self, folder=None):
        if folder is None:
            folder = self.folder
        return ManageChannels(folder, self.app.REQUEST)

    def test_has_container(self):
        view = self.makeView()
        self.assertFalse(view.hasContainer())

        addRSSChannelContainer(self.folder)
        view = self.makeView()
        self.assertTrue(view.hasContainer())

    @staticmethod
    def extractChannels(view):
        # call the view API and present channels as dicts for easy assert
        # why staticmethod ? for fun
        return tuple(dict(id=chan.getId(), title=chan.title)
                     for chan in view.channels(with_activation=False))

    def test_channels(self):
        view = self.makeView()
        self.assertEquals(view.channels(), ())

        container = addRSSChannelContainer(self.folder)
        view = self.makeView()
        view.addChannel(url=get_feed_url('zope.rss'))
        view.addChannel(url=get_feed_url('trac_cps.rss'))

        self.assertEquals(self.extractChannels(view),
                          (dict(id='zope-org', title='Zope.org'),
                           dict(id='cps-cms-ticket-query',
                                title='CPS CMS: Ticket Query')))

    def test_addChannel_form_no_cont(self):
        # test adding a channel while there's no container yet, from form
        view = self.makeView()
        view.request.form['channel_url'] = get_feed_url('zope.rss')
        view.addChannel()

        self.assertEquals(self.extractChannels(view),
                          (dict(id='zope-org', title='Zope.org'),))

    def test_refresh(self):
        view = self.makeView()
        view.addChannel(url=get_feed_url('zope.rss'))

        # low level url change
        channel = view.channels(with_activation=False)[0]
        channel.channel_url = get_feed_url('trac_cps.rss')
        # before refresh
        self.assertEquals(channel.title, 'Zope.org')
        # after
        view.refresh()
        self.assertEquals(channel.title, 'CPS CMS: Ticket Query')

def test_suite():
    return unittest.makeSuite(ManageChannelsTestCase)
