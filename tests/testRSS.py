# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

import unittest, os.path
import CPSRSSTestCase

class TestRSSTool(CPSRSSTestCase.CPSRSSTestCase):
    def testEmptyTool(self):
        rss_tool = self.portal.portal_rss
        self.assertEquals(rss_tool.meta_type, 'RSS Tool')
        self.assertEquals(rss_tool.objectIds(), [])
        rss_tool.refresh()

    def _testChannel(self, lazy_refresh=0):
        rss_tool = self.portal.portal_rss
        rss_tool.lazy_refresh = lazy_refresh
        url = os.path.abspath(os.path.join(
            os.path.dirname(CPSRSSTestCase.__file__), 'zope.rss'))
        rss_tool.manage_addRSSChannel('channel', url)
        self.assertEquals(rss_tool.objectIds(), ['channel'])
        rss_tool.refresh()
        d = rss_tool.channel.getData()
        self.assertEquals(d['url'], 'http://zope.org')
        self.assertEquals(d['title'], 'Zope.org')
        self.assertEquals(d['description'], '')

    def testChannelLazy(self):
        self._testChannel(lazy_refresh=1)

    def testChannelNotLazy(self):
        self._testChannel(lazy_refresh=0)


def test_suite():
    suites = [unittest.makeSuite(TestRSSTool)]
    return unittest.TestSuite(suites)

if __name__=="__main__":
    unittest.main(defaultTest='test_suite')
