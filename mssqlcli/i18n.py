import gettext
import os
from importlib import import_module

MODULE_ROOT_DIR = os.path.dirname(import_module('mssqlcli').__file__)
DOMAIN = 'mssql-cli'
LOCALE_DIR = os.path.join(MODULE_ROOT_DIR, 'locale')
LANGUAGES = None

def translation(domain=DOMAIN, localedir=LOCALE_DIR, languages=None):
    languages = languages if (not languages is None) else LANGUAGES
    return gettext.translation(domain, localedir, languages, fallback=True)
