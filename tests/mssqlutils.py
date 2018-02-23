import mssqlcli.sqltoolsclient as sqltoolsclient
import mssqlcli.mssqlcliclient as mssqlcliclient

from mssqlcli.main import format_output, OutputSettings
from mssqlcli.mssqlclioptionsparser import get_parser
from argparse import Namespace


def create_mssql_cli_client(options=None, owner_uri=None, connect=True, sql_tools_client=None, **additional_params):
    """
    Retrieve a mssqlcliclient connection.
    :param owner_uri: string
    :param connect: boolean
    :param sql_tools_client: SqlToolsClient
    :param options: options
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

    parser = get_parser()
    default_mssql_cli_options = parser.parse_args('')

    if nondefault_options:
        updateable_mssql_cli_options = vars(default_mssql_cli_options)
        for option in nondefault_options.keys():
            if option not in updateable_mssql_cli_options.keys():
                raise Exception('Invalid mssql cli option specified {}'.format(option))

            updateable_mssql_cli_options[option] = nondefault_options.get(option)

        return Namespace(**updateable_mssql_cli_options)

    return default_mssql_cli_options


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

    for rows, col, message, query, is_error in client.execute_single_statement(sql):
        settings = OutputSettings(table_format='psql', dcmlfmt='d', floatfmt='g',
                                  expanded=expanded)
        formatted = format_output(None, rows, col, message, settings)
        if join:
            formatted = '\n'.join(formatted)

        return formatted


def shutdown(connection):
    connection.shutdown()
