import os
import socket
import warnings
from argparse import Namespace
import mssqlcli.sqltoolsclient as sqltoolsclient
import mssqlcli.mssqlcliclient as mssqlcliclient
from mssqlcli.mssql_cli import MssqlCli
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

def shutdown(connection):
    connection.shutdown()

def getTempPath(*args):
    testRoot = os.path.join(os.path.abspath(__file__), '..')
    tempPath = os.path.join(testRoot, 'temp')
    for arg in args:
        tempPath = os.path.join(tempPath, arg)
    return  os.path.abspath(tempPath)

def create_test_db():
    client = create_mssql_cli_client()
    local_machine_name = socket.gethostname().replace(
        '-', '_').replace('.', '_')
    test_db_name = u'mssqlcli_testdb_{0}_{1}'.format(
        local_machine_name, random_str())
    query_db_create = u"CREATE DATABASE {0};".format(test_db_name)
    count = 0

    # retry logic in case db create fails
    while count < 5:
        for _, _, status, _, is_create_error in client.execute_query(query_db_create):
            if not is_create_error:
                shutdown(client)
                return test_db_name
            # log warning to console
            warnings.warn('Test DB create failed with error: {0}'.format(status))
        count += 1
    shutdown(client)

    # cleanup db just in case, then raise exception
    clean_up_test_db(test_db_name)
    raise AssertionError("DB creation failed.")

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
