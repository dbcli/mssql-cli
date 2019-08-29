# -*- coding: utf-8 -*-
import unittest
import sys
import os
import mssqlcli.i18n as i18n
import shutil


class LocalizationTests(unittest.TestCase):

    def test_product(self):
        mo_config = {
            'extraction_target': i18n.MODULE_ROOT_DIR,
            'lang_name': 'ko_KR',
            'domain': i18n.DOMAIN,
            'trans_mappings': {
                u'Goodbye!': u'안녕히가세요!',
            }
        }
        i18n.generate_mo(mo_config)

        i18n.LANGUAGES = ['ko']
        from mssqlcli.mssql_cli import goodbyeStr
        actual = self.unicode(goodbyeStr())
        expected = u'안녕히가세요!'
        assert actual == expected


    def test_ko_KR(self):
        domain, ext = os.path.splitext(os.path.basename(__file__))
        mo_config = {
            'extraction_target': '{0}.py'.format(os.path.splitext(__file__)[0]),
            'lang_name': 'ko_KR',
            'domain': domain,
            'trans_mappings': {
                u'Goodbye!': u'안녕히가세요!',
                u'Hello~': u'안녕하세요~',
                u'I am very hungry.': u'나 많이 배고파.'
            }
        }

        domain, localedir = i18n.generate_mo(mo_config)
        _ = i18n.translation(domain, localedir, ['ko']).gettext
        
        actual = self.unicode(_(u'Goodbye!'))
        expected = u'안녕히가세요!'
        assert actual == expected

        actual = self.unicode(_(u'Hello~'))
        expected = u'안녕하세요~'
        assert actual == expected

        actual = self.unicode(_(u'I am very hungry.'))
        expected = u'나 많이 배고파.'
        assert actual == expected

        shutil.rmtree(localedir)


    def unicode(self, s):
        if (sys.version_info.major < 3 and isinstance(s, str)):
            return s.decode('utf-8')
        return s
