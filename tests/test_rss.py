# (c) 2003 Nuxeo SARL <http://nuxeo.com>

import unittest, os.path

from OFS.Folder import Folder
from basetests import CPSRSSTestCase
from basetests import ZopeRSSTestCase
from basetests import get_feed_url

from Products.CPSRSS.RSSChannelContainer import RSSChannelContainer
from Products.CPSRSS.RSSChannelContainer import addRSSChannelContainer


class TestRSS(object):

    def localContainer(self):
        """Provided by subclasses."""
        raise NotImplementedError

    def testEmptyTool(self):
        rss_tool = self.tool
        self.assertEquals(rss_tool.meta_type, 'RSS Tool')
        self.assertEquals(rss_tool.objectIds(), [])
        rss_tool.refresh()

    def _testChannel(self, lazy_refresh=0):
        rss_tool = self.tool
        rss_tool.lazy_refresh = lazy_refresh

        rss_tool.manage_addRSSChannel('channel', get_feed_url('zope.rss'))
        self.assertEquals(rss_tool.objectIds(), ['channel'])
        channel = rss_tool.channel

        d = channel.getData()
        self.assertEquals(d['url'], 'http://zope.org')
        self.assertEquals(d['title'], 'Zope.org')
        self.assertEquals(d['description'], '')
        return channel

    def _testLocalChannel(self, lazy_refresh=0):
        rss_tool = self.tool
        rss_tool.lazy_refresh = lazy_refresh

        container = self.localContainer()
        container.manage_addRSSChannel('channel', get_feed_url('zope.rss'))
        self.assertEquals(container.objectIds(), ['channel'])
        channel = container.channel

        d = channel.getData()
        self.assertEquals(d['url'], 'http://zope.org')
        self.assertEquals(d['title'], 'Zope.org')
        self.assertEquals(d['description'], '')
        return container, channel

    def testChannelLazy(self):
        self._testChannel(lazy_refresh=1)

    def testChannelNotLazy(self):
        self._testChannel(lazy_refresh=0)

    def testLocalChannelLazy(self):
        self._testLocalChannel(lazy_refresh=1)

    def testLocalChannelNotLazy(self):
        self._testLocalChannel(lazy_refresh=0)

    def testExplicitRefresh(self):
        # this should eventually move to RSSChannelContainer tests
        self.tool.refresh_delay = 30
        # creating and filling the channel (TODO refactor)
        container, channel = self._testLocalChannel(lazy_refresh=1)
        channel.channel_url = get_feed_url('trac_cps.rss')
        # check that we'll actually test somethin
        self.assertEquals(channel.getData()['title'], 'Zope.org')
        container.refresh()
        self.assertEquals(channel.getData()['title'], 'CPS CMS: Ticket Query')


class CPSTestRSS(TestRSS, CPSRSSTestCase):
    """Run the tests in a full CPS portal context."""

    def localContainer(self):
        return addRSSChannelContainer(self.portal.workspaces)


class ZopeTestRSS(TestRSS, ZopeRSSTestCase):
    """Run the tests in a ZopeTestCase environment"""

    def localContainer(self):
        self.folder._setObject('subfold', Folder('subfold'))
        return addRSSChannelContainer(self.folder.subfold)


def test_suite():
    suites = [unittest.makeSuite(cls) for cls in (ZopeTestRSS, CPSTestRSS)]
    return unittest.TestSuite(suites)

if __name__=="__main__":
    unittest.main(defaultTest='test_suite')
