import os
import mssqlcli.sqltoolsclient as sqltoolsclient
import mssqlcli.mssqlcliclient as mssqlcliclient
from mssqlcli.main import format_output, OutputSettings


def create_mssql_cli_client(owner_uri=None, connect=True):
    """
    Retrieve a mssqlcliclient connection.
    :param owner_uri: string
    :param connect: boolean
    :param server_name: string
    :param database_name: string
    :return: MssqlCliClient
    """
    try:
        server_name = os.environ['MSSQL_CLI_SERVER']
        database_name = os.environ['MSSQL_CLI_DATABASE']
        user_name = os.environ['MSSQL_CLI_USER']
        password = os.environ['MSSQL_CLI_PASSWORD']

        if not server_name or not database_name or not user_name or not password:
            raise Exception('Environment variables for running tests not found.')

        sql_tools_client = sqltoolsclient.SqlToolsClient()
        mssql_cli_client = mssqlcliclient.MssqlCliClient(sql_tools_client,
                                                         server_name,
                                                         user_name,
                                                         password,
                                                         database=database_name,
                                                         owner_uri=owner_uri,
                                                         extra_bool_param=True,
                                                         extra_string_param=u'stringparam',
                                                         extra_int_param=5)
        if connect:
            mssql_cli_client.connect()
        return mssql_cli_client
    except Exception as e:
        print('Connection failed')
        raise e


def run_and_return_string_from_formatter(client, sql, join=False, expanded=False):
    """
    Return string output for the sql to be run
    :param client: MssqlCliClient
    :param sql: string
    :param join: boolean
    :param expanded: boolean
    :param exception_formatter: boolean
    :return:
    """

    for rows, col, message, query, is_error in client.execute_single_batch_query(sql):
        settings = OutputSettings(table_format='psql', dcmlfmt='d', floatfmt='g',
                                  expanded=expanded)
        formatted = format_output(None, rows, col, message, settings)
        if join:
            formatted = '\n'.join(formatted)

        return formatted


def shutdown(connection):
    connection.shutdown()
