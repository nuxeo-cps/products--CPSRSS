"""Unit tests for .po files

Adapted from plone-i18n

References:
http://i18n.kde.org/translation-howto/check-gui.html#check-msgfmt
http://cvs.sourceforge.net/viewcvs.py/plone-i18n/i18n/tests/
"""

import os, os.path, sys

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
import unittest
from glob import glob
from gettext import GNUTranslations
from msgfmt import Msgfmt, PoSyntaxError

_TESTS_PATH = os.path.split(__file__)[0]
if not _TESTS_PATH:
    _TESTS_PATH = '.'

try:
    import commands
except ImportError:
    if os.name != 'posix':
        raise ImportError("The i18n tests only runs on posix systems, \
                           such as Linux, \
               due to a dependency on Python's commands.getstatusoutput().")


def canonizeLang(lang):
    """Return a canonized language name so that language names can easily be
    compared.
    """
    return lang.lower().replace('_', '-')


def getLanguageFromPath(path):
    """Check that the same of the .po file corresponds to the contained
    translations.
    """
    # get file
    file = path.split('/')[-1]
    # strip of .po
    file = file[:-3]
    # This code was for CPSSkins which has .po of the form cpsskins-en.po
    #lang = file.split('-')[1:][-1:]
    #return '-'.join(lang)
    return file


def getPoPath():
    import Products
    product_file = getattr(Products, 'CPSRSS').__file__
    product_path = os.path.dirname(product_file)
    po_path = os.path.join(product_path, 'i18n')
    return po_path


def getPotFiles():
    po_path = getPoPath()
    po_files = [f for f in os.listdir(po_path) if f.endswith('.pot')]
    #print po_files
    return po_files


def getPoFiles():
    po_path = getPoPath()
    po_files = [f for f in os.listdir(po_path) if f.endswith('.po')]
    #print po_files
    return po_files


class TestPOT(ZopeTestCase.ZopeTestCase):
    potFile = None

    def testNoDuplicateMsgId(self):
        """Check that there are no duplicate msgid:s in the pot files"""
        cmd = 'grep ^msgid %s/../i18n/%s|sort|uniq --repeated' % (
            _TESTS_PATH, potFile)
        status = commands.getstatusoutput(cmd)
        assert len(status[1]) == 0, "Duplicate msgid:s were found:\n\n%s" \
                                     % status[1]


class TestPoFile(ZopeTestCase.ZopeTestCase):
    poFile = None

    def testPoFile(self):
        po = self.poFile
        poName = po
        file = open(os.path.join(getPoPath(), po), 'r')
        try:
            lines = file.readlines()
        except IOError, msg:
            self.fail('Can\'t read po file %s:\n%s' % (poName,msg))
        file.close()

        # Checking that the .po file has a non-fuzzy header entry, so that it
        # cannot be deleted by error.
        cmd = """grep -B 1 'msgid ""' %s/../i18n/%s|grep fuzzy""" % (
            _TESTS_PATH, poName)
        #print "cmd = %s" % cmd
        statusoutput = commands.getstatusoutput(cmd)
        #print "status = %s" % statusoutput[0]
        #print "output = %s" % statusoutput[1]
        self.assert_(statusoutput[0] != 0,
                     "Fuzzy header entry found in file %s! "
                     "Remove the fuzzy flag on this entry.\n\n%s"
                     % (poName, statusoutput[1]))

        try:
            mo = Msgfmt(lines)
        except PoSyntaxError, msg:
            self.fail('PoSyntaxError: Invalid po data syntax in file %s:\n%s' \
                      % (poName, msg))
        except SyntaxError, msg:
            self.fail('SyntaxError: Invalid po data syntax in file %s \
                      (Can\'t parse file with eval():\n%s' % (poName, msg))
        except Exception, msg:
            self.fail('Unknown error while parsing the po file %s:\n%s' \
                      % (poName, msg))

        try:
            tro = GNUTranslations(mo.getAsFile())
            #print "tro = %s" % tro
        except UnicodeDecodeError, msg:
            self.fail('UnicodeDecodeError in file %s:\n%s' % (poName, msg))
        except PoSyntaxError, msg:
            self.fail('PoSyntaxError: Invalid po data syntax in file %s:\n%s' \
                      % (poName, msg))

        domain = tro._info.get('domain', None)
        #print "domain = %s" % domain
        self.failUnless(domain, 'Po file %s has no domain!' % po)

        language_new = tro._info.get('language-code', None) # new way
        #print "language_new = %s" % language_new
        language_old = tro._info.get('language', None) # old way
        #print "language_old = %s" % language_old
        language = language_new or language_old

        self.failIf(language_old, 'The file %s has the old style language flag \
                                   set to %s. Please remove it!' \
                                  % (poName, language_old))

        self.failUnless(language, 'Po file %s has no language!' % po)

        fileLang = getLanguageFromPath(po)
        #print "getLanguageFromPath = %s" % fileLang
        fileLang = canonizeLang(fileLang)
        #print "canonizeLang = %s" % fileLang
        language = canonizeLang(language)
        #print "language canonizeLang(language) = %s" % language
        self.failUnless(fileLang == language,
            'The file %s has the wrong name or wrong language code. \
             expected: %s, got: %s' % \
             (poName, language, fileLang))

        # i18n completeness chart generation mechanism relies on case sensitive
        # Language-Code and Language-Name.
        for meta_info in ['"Language-Code: ',
                          '"Language-Name: ',
                          '"Domain: ',
                          ]:
            cmd = """grep '%s' %s/../i18n/%s""" % (
                meta_info, _TESTS_PATH, poName)
            #print "cmd = %s" % cmd
            statusoutput = commands.getstatusoutput(cmd)
            #print "status = %s" % statusoutput[0]
            #print "output = %s" % statusoutput[1]
            self.assert_(statusoutput[0] == 0,
                         "Wrong case used for metadata in file %s! "
                         "Check that your metadata is "
                         "Language-Code, Language-Name and Domain.\n\n%s"
                         % (poName, statusoutput[1]))


class TestMsg(ZopeTestCase.ZopeTestCase):
    poFile = None
    potFile = None

    def checkMsgExists(self,po,template):
        """Check that each existing message is translated and
           that there are no extra messages."""
        cmd='LC_ALL=C msgcmp --directory=%s/../i18n %s %s' % (
            _TESTS_PATH, po,template)
        status = commands.getstatusoutput(cmd)
        if status[0] != 0:
            return status
        return None


tests=[]
for potFile in getPotFiles():
    class TestOnePOT(TestPOT):
        potFile = potFile
    tests.append(TestOnePOT)

for poFile in getPoFiles():
    class TestOneMsg(TestMsg):
        poFile = poFile
    tests.append(TestOneMsg)

    class TestOnePoFile(TestPoFile):
        poFile = poFile
    tests.append(TestOnePoFile)


def test_suite():
    suite = unittest.TestSuite()
    for test in tests:
        suite.addTest(unittest.makeSuite(test))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)

