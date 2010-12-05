# (c) 2003 Nuxeo SARL <http://nuxeo.com>

import unittest, os.path

from OFS.Folder import Folder
from CPSRSSTestCase import CPSRSSTestCase
from CPSRSSTestCase import ZopeRSSTestCase

from Products.CPSRSS.RSSChannelContainer import RSSChannelContainer

def get_feed_url(feed_file):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), feed_file))


class TestRSS(object):

    def localContainer(self):
        """Depends on subclass."""
        raise NotImplementedError

    def _localContainer(self, folder):
        """Common code called by subclass."""
        folder._setObject('.cps_rss', RSSChannelContainer('.cps_rss'))
        return folder['.cps_rss']

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
        rss_tool.refresh()
        d = rss_tool.channel.getData()
        self.assertEquals(d['url'], 'http://zope.org')
        self.assertEquals(d['title'], 'Zope.org')
        self.assertEquals(d['description'], '')

    def _testLocalChannel(self, lazy_refresh=0):
        rss_tool = self.tool
        rss_tool.lazy_refresh = lazy_refresh

        container = self.localContainer()
        container.manage_addRSSChannel('channel', get_feed_url('zope.rss'))
        self.assertEquals(container.objectIds(), ['channel'])
        rss_tool.refresh()
        d = container.channel.getData()
        self.assertEquals(d['url'], 'http://zope.org')
        self.assertEquals(d['title'], 'Zope.org')
        self.assertEquals(d['description'], '')

    def testChannelLazy(self):
        self._testChannel(lazy_refresh=1)

    def testChannelNotLazy(self):
        self._testChannel(lazy_refresh=0)

    def testLocalChannelLazy(self):
        self._testLocalChannel(lazy_refresh=1)

    def testLocalChannelNotLazy(self):
        self._testLocalChannel(lazy_refresh=0)

class CPSTestRSS(TestRSS, CPSRSSTestCase):
    """Run the tests in a full CPS portal context."""

    def localContainer(self):
        return self._localContainer(self.portal.workspaces)


class ZopeTestRSS(TestRSS, ZopeRSSTestCase):
    """Run the tests in a ZopeTestCase environment"""

    def localContainer(self):
        self.folder._setObject('subfold', Folder('subfold'))
        return self._localContainer(self.folder.subfold)

def test_suite():
    suites = [unittest.makeSuite(cls) for cls in (ZopeTestRSS, CPSTestRSS)]
    return unittest.TestSuite(suites)

if __name__=="__main__":
    unittest.main(defaultTest='test_suite')
