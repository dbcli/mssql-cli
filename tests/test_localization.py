# -*- coding: utf-8 -*-
import unittest
import mssqlcli.localized_strings as localized
from mssqlcli.util import decode


class LocalizationTests(unittest.TestCase):

    @staticmethod
    def test_product():
        original = localized.goodbye()
        localized.translation(languages=['ko']).install()
        translated = decode(localized.goodbye())
        assert original != translated
