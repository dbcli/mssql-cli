# -*- coding: utf-8 -*-
import unittest
import mssqlcli.localized_strings as localized
from utility import decode


class LocalizationTests(unittest.TestCase):

    def test_product(self):
        original = localized.goodbye()
        localized.translation(languages=['ko']).install()
        translated = decode(localized.goodbye())
        assert original != translated
