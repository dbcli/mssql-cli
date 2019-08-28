# -*- coding: utf-8 -*-

import unittest
import os
import mssqlcli.i18n as i18n
import utility
import shutil
import polib
import sys


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
        self.generate_mo(mo_config)

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

        domain, localedir = self.generate_mo(mo_config)
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

    
    def generate_mo(self, mo_config):
        extraction_target = self.getValue(mo_config, 'extraction_target')
        extraction_dir = extraction_target if os.path.isdir(extraction_target) else os.path.dirname(extraction_target)

        localedir = self.getValue(mo_config, 'localedir')
        localedir = localedir if (not localedir is None) else os.path.join(extraction_dir, 'locale')
        lang_name = self.getValue(mo_config, 'lang_name')
        mo_dir = os.path.join(localedir, lang_name, 'LC_MESSAGES')
        self.create_dir([extraction_dir, 'locale', lang_name, 'LC_MESSAGES'])

        domain = self.getValue(mo_config, 'domain')
        pot_file = '{0}.pot'.format(os.path.join(localedir, domain))
        po_file = '{0}.po'.format(os.path.join(mo_dir, domain))
        mo_file = '{0}.mo'.format(os.path.join(mo_dir, domain))
        
        extract_command = "pybabel extract {0} -o {1}".format(extraction_target, pot_file)
        utility.exec_command(extract_command, extraction_dir)

        trans_mappings = self.getValue(mo_config, 'trans_mappings')
        po = polib.pofile(pot_file)
        for entry in po:
            if (entry.msgid in trans_mappings):
                entry.msgstr = trans_mappings[entry.msgid]
        po.save(po_file)
        po.save_as_mofile(mo_file)
        return domain, localedir


    def getValue(self, dict, key):
        try:
            return dict[key]
        except:
            return None


    def create_dir(self, path):
        curr_path = None
        for p in path:
            if (curr_path is None):
                curr_path = os.path.abspath(p)
            else:
                curr_path = os.path.join(curr_path, p)
            if (not os.path.exists(curr_path)):
                os.mkdir(curr_path)


    def unicode(self, s):
        if (sys.version_info.major < 3 and isinstance(s, str)):
            return s.decode('utf-8')
        return s
