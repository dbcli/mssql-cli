import os
from os.path import expanduser, exists, dirname

import shutil
import platform
from configobj import ConfigObj
from mssqlcli import __file__ as package_root


def config_location():
    if platform.system() == 'Windows':
        return os.getenv('LOCALAPPDATA') + '\\dbcli\\mssqlcli\\'

    if 'XDG_CONFIG_HOME' in os.environ:
        return '%s/mssqlcli/' % expanduser(os.environ['XDG_CONFIG_HOME'])

    return expanduser('~/.config/mssqlcli/')


def load_config(usr_cfg, def_cfg=None):
    cfg = ConfigObj()
    cfg.merge(ConfigObj(def_cfg, interpolation=False))
    cfg.merge(ConfigObj(expanduser(usr_cfg), interpolation=False, encoding='utf-8'))
    cfg.filename = expanduser(usr_cfg)

    return cfg


def ensure_dir_exists(path):
    parent_dir = expanduser(dirname(path))
    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir)


def write_default_config(source, destination, overwrite=False):
    destination = expanduser(destination)
    if not overwrite and exists(destination):
        return

    ensure_dir_exists(destination)

    shutil.copyfile(source, destination)


def upgrade_config(config, def_config):
    cfg = load_config(config, def_config)
    cfg.write()


def get_config(config_file=None):
    pkg_root = os.path.dirname(package_root)

    config_file = config_file or '%sconfig' % config_location()

    default_config = os.path.join(pkg_root, 'mssqlclirc')
    write_default_config(default_config, config_file)

    return load_config(config_file, default_config)


def get_casing_file(config):
    casing_file = config['main']['casing_file']
    if casing_file == 'default':
        casing_file = config_location() + 'casing'
    return casing_file
