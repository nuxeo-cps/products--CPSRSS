# (C) Copyright 2005 Nuxeo SARL <http://nuxeo.com>
# (C) Copyright 2005 Unilog <http://unilog.com>
# Authors:
# M.-A. Darche <madarche@nuxeo.com>
# G. de la Rochemace <gdelaroch@unilog.com>
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
# $Id: BaseBox.py 7293 2005-04-03 23:09:11Z janguenot $

"""Unit tests for .po files

Adapted from plone-i18n

References:
http://i18n.kde.org/translation-howto/check-gui.html#check-msgfmt
http://cvs.sourceforge.net/viewcvs.py/plone-i18n/i18n/tests/
"""

import os, os.path, sys, re

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
    product_name = __name__.split('.')[0]
    import Products
    product_file = getattr(Products, product_name).__file__
    product_path = os.path.dirname(product_file)
    po_path = os.path.join(product_path, 'i18n')
    return po_path


def getPotFiles():
    po_path = getPoPath()
    po_files = [f for f in os.listdir(po_path) if f.endswith('.pot')]
    return po_files


def getPoFiles():
    po_path = getPoPath()
    po_files = [f for f in os.listdir(po_path) if f.endswith('.po')]
    return po_files



# DOTALL: Make the "." special character match any character at all, including a
# newline; without this flag, "." will match anything except a newline.
#
# for example:
#
# msgid "button_back"
# msgstr ""
#
# returns 'button_back'
#
MSGID_REGEXP = re.compile('msgid "(.*?)".*?msgstr "', re.DOTALL)

class TestPOT(ZopeTestCase.ZopeTestCase):
    pot_filename = None

    def testNoDuplicateMsgId(self):
        """Check that there are no duplicate msgid:s in the pot files"""

        pot = self.pot_filename
        
        file = open(os.path.join(getPoPath(), pot), 'r')
        file_content = file.read()
        file.close()

        # Check for duplicate msgids
        matches = re.finditer(MSGID_REGEXP, file_content)
        
        msgids = []

        for match in matches:
            msgid = match.group(0)
            if msgid in msgids:
                assert 0, "Duplicate msgid:s were found in the file %s :\n\n%s" \
                       % (pot, msgid)
            else:
                msgids.append(msgid)


# DOTALL: Make the "." special character match any character at all, including a
# newline; without this flag, "." will match anything except a newline.
#
# #, fuzzy
# msgid ""
# msgstr ""
#
FUZZY_HEADER_ENTRY_REGEXP = re.compile('#, fuzzy\nmsgid ""\nmsgstr ""',
                                       re.DOTALL)

# IGNORECASE: Perform case-insensitive matching; expressions like [A-Z] will
# match lowercase letters, too. This is not affected by the current locale.
#
# MULTILINE: When specified, the pattern character "^" matches at the beginning
# of the string and at the beginning of each line (immediately following each
# newline); and the pattern character "$" matches at the end of the string and
# at the end of each line (immediately preceding each newline). By default, "^"
# matches only at the beginning of the string, and "$" only at the end of the
# string and immediately before the newline (if any) at the end of the string.
#
# Check the charset:
#
# for example
#
# "Content-Type: text/plain; charset=ISO-8859-15\n"
#
CHARSET_REGEXP = re.compile('^"Content-Type: text/plain; charset=ISO-8859-15',
                            re.MULTILINE | re.IGNORECASE)

class TestPoFile(ZopeTestCase.ZopeTestCase):
    po_filename = None

    def testPoFile(self):
        po = self.po_filename

        po_name = po
        file = open(os.path.join(getPoPath(), po), 'r')
        file_content = file.read()
        file.seek(0)
        try:
            lines = file.readlines()
        except IOError, msg:
            self.fail('Can\'t read po file %s:\n%s' % (po_name, msg))
        file.close()

        # Checking that the .po file has a non-fuzzy header entry, so that it
        # cannot be deleted by error.
        match_fuzzy = re.findall(FUZZY_HEADER_ENTRY_REGEXP, file_content)
     
        match_charset = re.findall(CHARSET_REGEXP, file_content)

        if len(match_fuzzy) != 0:
            assert 0, "Fuzzy header entry found in file %s! " \
               "Remove the fuzzy flag on this entry.\n\n" \
               % po_name
 
        if len(match_charset) != 1:
            assert 0, "Invalide charset found in file %s! \n the correct " \
               "line is : 'Content-Type: text/plain; charset=ISO-8859-15'\n\n" \
               % po_name

        try:
            mo = Msgfmt(lines)
        except PoSyntaxError, msg:
            self.fail('PoSyntaxError: Invalid po data syntax in file %s:\n%s' \
                      % (po_name, msg))
        except SyntaxError, msg:
            self.fail('SyntaxError: Invalid po data syntax in file %s \
                      (Can\'t parse file with eval():\n%s' % (po_name, msg))
        except Exception, msg:
            self.fail('Unknown error while parsing the po file %s:\n%s' \
                      % (po_name, msg))

        try:
            tro = GNUTranslations(mo.getAsFile())
            #print "tro = %s" % tro
        except UnicodeDecodeError, msg:
            self.fail('UnicodeDecodeError in file %s:\n%s' % (po_name, msg))
        except PoSyntaxError, msg:
            self.fail('PoSyntaxError: Invalid po data syntax in file %s:\n%s' \
                      % (po_name, msg))

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
                                  % (po_name, language_old))

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
             (po_name, language, fileLang))

        # i18n completeness chart generation mechanism relies on case sensitive
        # Language-Code and Language-Name.
        for meta_info in ['"Language-Code: ',
                          '"Language-Name: ',
                          '"Domain: ',
                          ]:
            cmd = """grep '%s' %s/../i18n/%s""" % (
                meta_info, _TESTS_PATH, po_name)
            #print "cmd = %s" % cmd
            statusoutput = commands.getstatusoutput(cmd)
            #print "status = %s" % statusoutput[0]
            #print "output = %s" % statusoutput[1]
            self.assert_(statusoutput[0] == 0,
                         "Wrong case used for metadata in file %s! "
                         "Check that your metadata is "
                         "Language-Code, Language-Name and Domain.\n\n%s"
                         % (po_name, statusoutput[1]))


class TestMsg(ZopeTestCase.ZopeTestCase):
    po_filename = None
    pot_filename = None

    def checkMsgExists(self,po,template):
        """Check that each existing message is translated and
           that there are no extra messages."""
        cmd = 'LC_ALL=C msgcmp --directory=%s/../i18n %s %s' % (
            TESTS_PATH, po,template)
        status = commands.getstatusoutput(cmd)
        if status[0] != 0:
            return status
        return None


tests = []
for pot_filename in getPotFiles():
    class TestOnePOT(TestPOT):
        pot_filename = pot_filename
    tests.append(TestOnePOT)

for po_filename in getPoFiles():
    class TestOneMsg(TestMsg):
        po_filename = po_filename
    tests.append(TestOneMsg)

    class TestOnePoFile(TestPoFile):
        po_filename = po_filename
    tests.append(TestOnePoFile)


def test_suite():
    suite = unittest.TestSuite()
    for test in tests:
        suite.addTest(unittest.makeSuite(test))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=2)

