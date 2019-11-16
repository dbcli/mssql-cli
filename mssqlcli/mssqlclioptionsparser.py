import argparse
import os
import mssqlcli

from .config import config_location

MSSQL_CLI_USER = u'MSSQL_CLI_USER'
MSSQL_CLI_PASSWORD = u'MSSQL_CLI_PASSWORD'
MSSQL_CLI_DATABASE = u'MSSQL_CLI_DATABASE'
MSSQL_CLI_SERVER = u'MSSQL_CLI_SERVER'
MSSQL_CLI_ROW_LIMIT = u'MSSQL_CLI_ROW_LIMIT'
MSSQL_CLI_RC = u'MSSQL_CLI_RC'


def create_parser():
    args_parser = argparse.ArgumentParser(
        prog=u'mssql-cli',
        description=u'Microsoft SQL Server CLI. ' +
        u'Version {}'.format(mssqlcli.__version__))

    args_parser.add_argument(
        u'-U', u'--username',
        dest=u'username',
        default=os.environ.get(MSSQL_CLI_USER, None),
        metavar=u'',
        help=u'Username to connect to the database')

    args_parser.add_argument(
        u'-P', u'--password',
        dest=u'password',
        default=os.environ.get(MSSQL_CLI_PASSWORD, None),
        metavar=u'',
        help=u'If not supplied, defaults to value in environment variable MSSQL_CLI_PASSWORD.')

    args_parser.add_argument(
        u'-d', u'--database',
        dest=u'database',
        default=os.environ.get(MSSQL_CLI_DATABASE, None),
        metavar=u'',
        help=u'database name to connect to.')

    args_parser.add_argument(
        u'-S', u'--server',
        dest=u'server',
        default=os.environ.get(MSSQL_CLI_SERVER, u'localhost'),
        metavar=u'',
        help=u'SQL Server instance name or address.')

    args_parser.add_argument(
        u'-E', u'--integrated',
        dest=u'integrated_auth',
        action=u'store_true',
        default=False,
        help=u'Use integrated authentication on windows.')

    args_parser.add_argument(
        u'-v', u'--version',
        dest=u'version',
        action=u'store_true',
        default=False,
        help=u'Version of mssql-cli.')

    args_parser.add_argument(
        u'--mssqlclirc',
        dest=u'mssqlclirc_file',
        default=os.environ.get(MSSQL_CLI_RC, config_location() + 'config'),
        metavar=u'',
        help=u'Location of mssqlclirc config file.')

    args_parser.add_argument(
        u'--row-limit',
        dest=u'row_limit',
        default=os.environ.get(MSSQL_CLI_ROW_LIMIT, None),
        metavar=u'',
        help=u'Set threshold for row limit prompt. Use 0 to disable prompt.')

    args_parser.add_argument(
        u'--less-chatty',
        dest=u'less_chatty',
        action=u'store_true',
        default=False,
        help=u'Skip intro on startup and goodbye on exit.')

    args_parser.add_argument(
        u'--auto-vertical-output',
        dest=u'auto_vertical_output',
        action=u'store_true',
        default=False,
        help=(u'Automatically switch to vertical output mode if the result is wider ' +
              'than the terminal width.'))

    args_parser.add_argument(
        u'-N', u'--encrypt',
        dest=u'encrypt',
        action=u'store_true',
        default=False,
        help=(u'SQL Server uses SSL encryption for all data if the server has a ' +
              'certificate installed.'))

    args_parser.add_argument(
        u'-C', u'--trust-server-certificate',
        dest=u'trust_server_certificate',
        action=u'store_true',
        default=False,
        help=(u'The channel will be encrypted while bypassing walking the certificate ' +
              'chain to validate trust.'))

    args_parser.add_argument(
        u'-l', u'--connect-timeout',
        dest=u'connection_timeout',
        default=0,
        metavar=u'',
        help=u'Time in seconds to wait for a connection to the server before terminating request.')

    args_parser.add_argument(
        u'-K', u'--application-intent',
        dest=u'application_intent',
        metavar=u'',
        help=(u'Declares the application workload type when connecting to a database in a SQL ' +
              'Server Availability Group.'))

    args_parser.add_argument(
        u'-M', u'--multi-subnet-failover',
        dest=u'multi_subnet_failover',
        action=u'store_true',
        default=False,
        help=(u'If application is connecting to AlwaysOn AG on different subnets, setting this ' +
              'provides faster detection and connection to currently active server.'))

    args_parser.add_argument(
        u'-a', u'--packet-size',
        dest=u'packet_size',
        default=0,
        metavar=u'',
        help=u'Size in bytes of the network packets used to communicate with SQL Server.')

    args_parser.add_argument(
        u'-A', u'--dac-connection',
        dest=u'dac_connection',
        action=u'store_true',
        default=False,
        help=u'Connect to SQL Server using the dedicated administrator connection.')

    args_parser.add_argument(
        u'-Q', u'--query',
        dest=u'query',
        metavar=u'',
        default=False,
        help=u'Executes a query outputting the results to stdout and exits.'
    )

    args_parser.add_argument(
        u'-i', u'--input_file',
        dest=u'input_file',
        metavar=u'',
        default=False,
        help=u'Specifies the file that contains a batch of SQL statements for processing.'
    )

    args_parser.add_argument(
        u'-o', u'--output_file',
        dest=u'output_file',
        metavar=u'',
        default=False,
        help=u'Specifies the file that receives output from a query.'
    )

    args_parser.add_argument(
        u'--enable-sqltoolsservice-logging',
        dest=u'enable_sqltoolsservice_logging',
        action=u'store_true',
        default=False,
        help=u'Enables diagnostic logging for the SqlToolsService.')

    args_parser.add_argument(
        u'--prompt',
        dest=u'prompt',
        metavar=u'',
        help=u'Prompt format (Default: \\d> ')

    args_parser.add_argument(
        u'--interactive_mode',
        dest=u'interactive_mode',
        metavar=u'',
        default=True,
        help=argparse.SUPPRESS
    )

    return args_parser
