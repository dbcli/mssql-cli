import os
import socket
import time
import warnings
from argparse import Namespace
import mssqlcli.sqltoolsclient as sqltoolsclient
import mssqlcli.mssqlcliclient as mssqlcliclient
from mssqlcli.mssql_cli import MssqlCli
from mssqlcli.config import get_config
from mssqlcli.mssqlclioptionsparser import create_parser
from utility import random_str


_BASELINE_DIR = os.path.dirname(os.path.abspath(__file__))

# test queries mapped to files
test_queries = [
    ("SELECT 1", 'small.txt'),
    ("SELECT 1; SELECT 2;", 'multiple.txt'),
    ("SELECT %s" % ('x' * 250), 'col_too_wide.txt'),
    ("SELECT REPLICATE(CAST('X,' AS VARCHAR(MAX)), 1024)", 'col_wide.txt')
]

def create_mssql_cli(**non_default_options):
    mssqlcli_options = create_mssql_cli_options(**non_default_options)
    mssql_cli = MssqlCli(mssqlcli_options)

    return mssql_cli

def create_mssql_cli_client(options=None, owner_uri=None, connect=True, sql_tools_client=None,
                            **additional_params):
    """
    Retrieve a mssqlcliclient connection.
    :param options: options
    :param owner_uri: string
    :param connect: boolean
    :param sql_tools_client: SqlToolsClient
    :param additional_params: kwargs
    :return: MssqlCliClient
    """
    try:
        sql_tools_client = sql_tools_client if sql_tools_client else sqltoolsclient.SqlToolsClient()
        mssql_cli_options = options if options else create_mssql_cli_options()

        mssql_cli_client = mssqlcliclient.MssqlCliClient(mssql_cli_options,
                                                         sql_tools_client,
                                                         owner_uri=owner_uri,
                                                         **additional_params)

        if connect:
            mssql_cli_client.connect_to_database()
        return mssql_cli_client
    except Exception as e:
        print('Connection failed')
        raise e

def create_mssql_cli_options(**nondefault_options):

    parser = create_parser()

    default_mssql_cli_options = parser.parse_args('')

    if nondefault_options:
        updateable_mssql_cli_options = vars(default_mssql_cli_options)
        for option, value in nondefault_options.items():
            if option not in updateable_mssql_cli_options.keys():
                raise Exception('Invalid mssql-cli option specified: {}'.format(option))

            updateable_mssql_cli_options[option] = value

        return Namespace(**updateable_mssql_cli_options)

    return default_mssql_cli_options

def create_mssql_cli_config(options=None):
    """
    Create config from options.
    """
    if not options:
        options = create_mssql_cli_options()
    return get_config(options.mssqlclirc_file)

def shutdown(connection):
    connection.shutdown()

def getTempPath(*args):
    testRoot = os.path.join(os.path.abspath(__file__), '..')
    tempPath = os.path.join(testRoot, 'temp')
    for arg in args:
        tempPath = os.path.join(tempPath, arg)
    return  os.path.abspath(tempPath)

def create_test_db():
    """
    Creates database for test, using various status checks and retry logic for reliability.
    - Uses outer while loop to retry db create failures
    - Uses an inner while loop to keep checking status if still processing
    - Exits on successful response
    """
    client = create_mssql_cli_client()
    local_machine_name = socket.gethostname().replace(
        '-', '_').replace('.', '_')

    # retry logic in case db create fails
    count_outer = 0
    while count_outer < 5:
        test_db_name = u'mssqlcli_testdb_{0}_{1}'.format(
            local_machine_name, random_str())
        query_db_create = u"CREATE DATABASE {0};".format(test_db_name)

        for _, _, status, _, is_create_error in client.execute_query(query_db_create):
            if is_create_error:
                # log warning to console and cleanup db
                warnings.warn('Test DB create failed with error: {0}'.format(status))
                clean_up_test_db(test_db_name)
            else:
                # check if create db is still processing. if so, continue to check on it for
                # another 5 tries
                count_inner = 0
                while count_inner < 5:
                    create_db_status = check_create_test_db_status(test_db_name, client)
                    if create_db_status == 'COMPLETED':
                        # created successfully
                        shutdown(client)
                        return test_db_name

                    if create_db_status == 'PROCESSING':
                        # sleep for 5 seconds and try again
                        time.sleep(5)
                        count_inner += 1
                    else:
                        # db create failed, cleanup db, and exit inner while loop
                        warnings.warn('Test DB create failed. Evaluated from ' \
                                      'sys.dm_operation_status.')
                        clean_up_test_db(test_db_name)
                        break
        count_outer += 1
    shutdown(client)

    # cleanup db just in case, then raise exception
    clean_up_test_db(test_db_name)
    raise AssertionError("DB creation failed.")

def check_create_test_db_status(db_name, client):
    """ Checks if database create is still being processed. """
    query_check_status = u"SELECT TOP 1 state_desc FROM sys.dm_operation_status " \
                         u"WHERE major_resource_id = '{}' AND operation = 'CREATE DATABASE' " \
                         u"ORDER BY start_time DESC".format(db_name)
    for row, _, _, _, _ in client.execute_query(query_check_status):
        return row[0][0]

def clean_up_test_db(test_db_name):
    client = create_mssql_cli_client()
    query = u"DROP DATABASE {0};".format(test_db_name)
    success = True
    for _, _, _, _, is_error in client.execute_query(query):
        if is_error is True:
            success = False
    shutdown(client)
    return success

def get_file_contents(file_path):
    """ Get expected result from file. """
    try:
        with open(file_path, 'r') as f:
            # remove string literals (needed in python2) and newlines
            return f.read().replace('\r', '').strip()
    except OSError as e:
        raise e

def get_io_paths(test_file_suffix):
    """ Returns tuple of file paths for the input and output of a test. """
    i = os.path.join(_BASELINE_DIR, 'test_query_inputs', 'input_%s' % test_file_suffix)
    o = os.path.join(_BASELINE_DIR, 'test_query_baseline', 'baseline_%s' % test_file_suffix)
    return (i, o)
