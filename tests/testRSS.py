# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

import unittest
import CPSRSSTestCase

class TestRSS(CPSRSSTestCase.CPSRSSTestCase):

    def testTool(self):
        self.portal.portal_rss


def test_suite():
    suites = [unittest.makeSuite(TestRSS)]
    return unittest.TestSuite(suites)

if __name__=="__main__":
    unittest.main(defaultTest='test_suite')
