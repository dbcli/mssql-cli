import gettext
import os
from importlib import import_module
import utility
import polib


MODULE_ROOT_DIR = os.path.dirname(import_module('mssqlcli').__file__)
DOMAIN = 'mssql-cli'
LOCALE_DIR = os.path.join(MODULE_ROOT_DIR, 'locale')
LANGUAGES = None


def translation(domain=DOMAIN, localedir=LOCALE_DIR, languages=None):
    languages = languages if (not languages is None) else LANGUAGES
    return gettext.translation(domain, localedir, languages, fallback=True)


def generate_mo(mo_config):
    extraction_target = getDictValue(mo_config, 'extraction_target')
    extraction_dir = extraction_target if os.path.isdir(extraction_target) else os.path.dirname(extraction_target)

    localedir = getDictValue(mo_config, 'localedir')
    localedir = localedir if (not localedir is None) else os.path.join(extraction_dir, 'locale')
    lang_name = getDictValue(mo_config, 'lang_name')
    mo_dir = os.path.join(localedir, lang_name, 'LC_MESSAGES')
    create_dir([extraction_dir, 'locale', lang_name, 'LC_MESSAGES'])

    domain = getDictValue(mo_config, 'domain')
    pot_file = '{0}.pot'.format(os.path.join(localedir, domain))
    po_file = '{0}.po'.format(os.path.join(mo_dir, domain))
    mo_file = '{0}.mo'.format(os.path.join(mo_dir, domain))
    
    extract_command = "pybabel extract {0} -o {1}".format(extraction_target, pot_file)
    utility.exec_command(extract_command, extraction_dir)

    trans_mappings = getDictValue(mo_config, 'trans_mappings')
    po = polib.pofile(pot_file)
    for entry in po:
        if (entry.msgid in trans_mappings):
            entry.msgstr = trans_mappings[entry.msgid]
    po.save(po_file)
    po.save_as_mofile(mo_file)
    return domain, localedir


def getDictValue(dict, key):
    try:
        return dict[key]
    except:
        return None


def create_dir(path):
    curr_path = None
    for p in path:
        if (curr_path is None):
            curr_path = os.path.abspath(p)
        else:
            curr_path = os.path.join(curr_path, p)
        if (not os.path.exists(curr_path)):
            os.mkdir(curr_path)