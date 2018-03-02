import mssqlcli.sqltoolsclient as sqltoolsclient
import mssqlcli.mssqlcliclient as mssqlcliclient

from argparse import Namespace
from mssqlcli.mssql_cli import MssqlCli
from mssqlcli.mssqlclioptionsparser import create_parser


def create_mssql_cli(**non_default_options):
    mssqlcli_options = create_mssql_cli_options(**non_default_options)
    mssql_cli = MssqlCli(mssqlcli_options)

    return mssql_cli


def create_mssql_cli_client(options=None, owner_uri=None, connect=True, sql_tools_client=None, **additional_params):
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
        for option in nondefault_options.keys():
            if option not in updateable_mssql_cli_options.keys():
                raise Exception('Invalid mssql-cli option specified: {}'.format(option))

            updateable_mssql_cli_options[option] = nondefault_options.get(option)

        return Namespace(**updateable_mssql_cli_options)

    return default_mssql_cli_options


def shutdown(connection):
    connection.shutdown()
