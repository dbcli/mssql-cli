# -*- coding: utf-8 -*-
import unittest
import sys
import mssqlcli.localized_strings as localized


class LocalizationTests(unittest.TestCase):

    def test_product(self):
        original = self.unicode(localized.goodbye())
        localized.translation(languages=['ko']).install()
        translated = self.unicode(localized.goodbye())
        assert original != translated
        
    def unicode(self, s):
        if (sys.version_info.major < 3 and isinstance(s, str)):
            return s.decode('utf-8')
        return s
