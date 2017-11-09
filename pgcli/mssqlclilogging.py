import logging
import logging.handlers
import os


def get_config_log_dir():
    """
        Retrieve logging directory, create it if it doesn't exist.
    """
    log_dir = os.path.expanduser(os.path.join(u'~', u'.mssqlcli'))
    if (not os.path.exists(log_dir)):
        os.makedirs(log_dir)
    return log_dir


def get_config_log_file():
    """
        Retrieve log file path.
    """
    return os.path.join(get_config_log_dir(), u'mssql-cli.log')


def initialize_logger():
    """
        Initializes root logger for scripter with rotating file handler. Should only be called once from main program.
    """
    scripter_logger = logging.getLogger('mssqlcli')
    scripter_logger.setLevel(logging.DEBUG)
    handler = logging.handlers.RotatingFileHandler(
        get_config_log_file(), maxBytes=2 * 1024 * 1024, backupCount=10)

    formatter = logging.Formatter(
        u'%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    scripter_logger.addHandler(handler)
