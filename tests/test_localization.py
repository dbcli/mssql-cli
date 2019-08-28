# -*- coding: utf-8 -*-

import unittest
import os
from mssqlcli.i18n import translate
import utility
import shutil

class LocalizationTests(unittest.TestCase):
    
    def test_ko_KR(self):
        domain, ext = os.path.splitext(os.path.basename(__file__))
        mo_config = {
            'base_dir': os.path.dirname(__file__),
            'lang_name': 'ko_KR',
            'domain': domain,
            'trans_mappings': [
                (u'Goodbye!', u'안녕히가세요!'),
                (u'Hello~', u'안녕하세요~'),
                (u'I am very hungry.', u'나 많이 배고파.')
            ]
        }

        domain, localedir = self.generate_mo(mo_config)
        _ = translate(domain, localedir, ['ko'])
        
        actual = _(u'Goodbye!').decode('utf-8')
        expected = u'안녕히가세요!'
        assert actual == expected

        actual = _(u'Hello~').decode('utf-8')
        expected = u'안녕하세요~'
        assert actual == expected

        actual = _(u'I am very hungry.').decode('utf-8')
        expected = u'나 많이 배고파.'
        assert actual == expected

        shutil.rmtree(localedir)

    
    def generate_mo(self, mo_config):
        base_dir = mo_config['base_dir']
        localedir = os.path.join(base_dir, 'locale')
        lang_name = mo_config['lang_name']
        mo_dir = os.path.join(localedir, lang_name, 'LC_MESSAGES')
        self.create_dir([base_dir, 'locale', lang_name, 'LC_MESSAGES'])

        try:
            import babel
        except ImportError:
            utility.exec_command('pip install --upgrade babel', utility.ROOT_DIR)

        domain = mo_config['domain']
        current_file = '{0}.py'.format(os.path.join(base_dir, domain))
        pot_file = '{0}.pot'.format(os.path.join(localedir, domain))
        po_file = '{0}.po'.format(os.path.join(mo_dir, domain))
        mo_file = '{0}.mo'.format(os.path.join(mo_dir, domain))
        
        extract_command = "pybabel extract {0} -o {1}".format(current_file, pot_file)
        utility.exec_command(extract_command, base_dir)

        trans_mappings = mo_config['trans_mappings']
        with open(pot_file, 'r') as t:
            content = t.read().encode('utf-8')
            print(type(content))
            py = content.replace('#\n#, fuzzy', '')
            for m in trans_mappings:
                original_msg = m[0]
                trans_before = u'msgid "{0}"\nmsgstr ""'.format(original_msg)
                trans_after = u'msgid "{0}"\nmsgstr "{1}"'.format(original_msg, m[1])
                py = py.replace(trans_before, trans_after)
            py = py.encode('utf-8')
            print(py)

        with open(po_file, 'w') as p:
            p.write(py)

        extract_command = "pybabel compile -i {0} -o {1}".format(po_file, mo_file)
        utility.exec_command(extract_command, mo_dir)
        return domain, localedir


    def create_dir(self, path):
        curr_path = None
        for p in path:
            if (curr_path is None):
                curr_path = os.path.abspath(p)
            else:
                curr_path = os.path.join(curr_path, p)
            print(curr_path)
            if (not os.path.exists(curr_path)):
                os.mkdir(curr_path)
