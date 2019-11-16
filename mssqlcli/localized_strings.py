import gettext
import os
from importlib import import_module

PATH = '{0}.py'.format(os.path.splitext(__file__)[0])
DOMAIN = 'mssql-cli'
LOCALE_DIR = os.path.join(os.path.dirname(__file__), 'locale')
LANGUAGES = None

def translation(domain=DOMAIN, localedir=LOCALE_DIR, languages=None):
    languages = languages if (not languages is None) else LANGUAGES
    return gettext.translation(domain, localedir, languages, fallback=True)

translation().install()


## Localized Strings
def goodbye():
    return _(u'Goodbye!')
