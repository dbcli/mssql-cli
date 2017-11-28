import logging
import logging.handlers
import os
from pgcli.config import config_location


def get_config_log_dir():
    """
        Retrieve logging directory, create it if it doesn't exist.
    """
    return config_location()


def get_config_log_file():
    """
        Retrieve log file path.
    """
    return os.path.join(get_config_log_dir(), u'mssqlcli.log')


def initialize_logger():
    """
        Initializes root logger for mssql-cli with rotating file handler. Should only be called once from main program.
    """
    mssqlcli_logger = logging.getLogger('mssqlcli')
    mssqlcli_logger.setLevel(logging.DEBUG)
    handler = logging.handlers.RotatingFileHandler(
        get_config_log_file(), maxBytes=2 * 1024 * 1024, backupCount=10)

    formatter = logging.Formatter(
        u'%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    mssqlcli_logger.addHandler(handler)
