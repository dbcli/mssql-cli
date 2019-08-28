import gettext
import os
from importlib import import_module

BASE_DIR = os.path.dirname(import_module('mssqlcli').__file__)
LOCALE_DIR = os.path.join(BASE_DIR, 'locale')
DOMAIN = 'mssql-cli'

def translate(domain=DOMAIN, localedir=LOCALE_DIR, languages=None):
    return gettext.translation(domain, localedir, languages=languages, fallback=True).gettext
