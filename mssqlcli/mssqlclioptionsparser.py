import argparse
import mssqlcli
import os

from .config import config_location

MSSQL_CLI_USER = u'MSSQL_CLI_USER'
MSSQL_CLI_PASSWORD = u'MSSQL_CLI_PASSWORD'
MSSQL_CLI_DATABASE = u'MSSQL_CLI_DATABASE'
MSSQL_CLI_SERVER = u'MSSQL_CLI_SERVER'
MSSQL_CLI_ROW_LIMIT = u'MSSQL_CLI_ROW_LIMIT'
MSSQL_CLI_RC = u'MSSQL_CLI_RC'


def initialize():
    parser = argparse.ArgumentParser(
        prog=u'mssql-cli',
        description=u'Microsoft SQL Server CLI. ' +
        u'Version {}'.format(mssqlcli.__version__))

    parser.add_argument(
        u'-U', u'--username',
        dest=u'username',
        default=os.environ.get(MSSQL_CLI_USER, None),
        metavar=u'',
        help=u'Username to connect to the database')

    parser.add_argument(
        u'-P', u'--password',
        dest=u'password',
        default=os.environ.get(MSSQL_CLI_PASSWORD, None),
        metavar=u'',
        help=u'If not supplied, defaults to value in environment variable MSSQL_CLI_PASSWORD.')

    parser.add_argument(
        u'-d', u'--database',
        dest=u'database',
        default=os.environ.get(MSSQL_CLI_DATABASE, u'master'),
        metavar=u'',
        help=u'database name to connect to.')

    parser.add_argument(
        u'-S', u'--server',
        dest=u'server',
        default=os.environ.get(MSSQL_CLI_SERVER, u'localhost'),
        metavar=u'',
        help=u'SQL Server instance name or address.')

    parser.add_argument(
        u'-I', u'--integrated',
        dest=u'integrated_auth',
        action=u'store_true',
        default=False,
        help=u'Use integrated authentication on windows.')

    parser.add_argument(
        u'-v', u'--version',
        dest=u'version',
        action=u'store_true',
        default=False,
        help=u'Version of mssql-cli.')

    parser.add_argument(
        u'--mssqlclirc',
        dest=u'mssqlclirc_file',
        default=os.environ.get(MSSQL_CLI_RC, config_location() + 'config'),
        metavar=u'',
        help=u'Location of mssqlclirc config file.')

    parser.add_argument(
        u'--row-limit',
        dest=u'row_limit',
        default=os.environ.get(MSSQL_CLI_ROW_LIMIT, None),
        metavar=u'',
        help=u'Set threshold for row limit prompt. Use 0 to disable prompt.')

    parser.add_argument(
        u'--less-chatty',
        dest=u'less_chatty',
        action=u'store_true',
        default=False,
        help=u'Skip intro on startup and goodbye on exit.')

    parser.add_argument(
        u'--auto-vertical-output',
        dest=u'auto_vertical_output',
        action=u'store_true',
        default=False,
        help=u'Automatically switch to vertical output mode if the result is wider than the terminal width.')

    parser.add_argument(
        u'-N', u'--encrypt',
        dest=u'encrypt',
        action=u'store_true',
        default=False,
        help=u'SQL Server uses SSL encryption for all data if the server has a certificate installed.')

    parser.add_argument(
        u'-C', u'--trust-server-certificate',
        dest=u'trust_server_certificate',
        action=u'store_true',
        default=False,
        help=u'The channel will be encrypted while bypassing walking the certificate chain to validate trust.')

    parser.add_argument(
        u'-l', u'--connect-timeout',
        dest=u'connection_timeout',
        default=0,
        metavar=u'',
        help=u'Time in seconds to wait for a connection to the server before terminating request.')

    parser.add_argument(
        u'-K', u'--application-intent',
        dest=u'application_intent',
        metavar=u'',
        help=u'Declares the application workload type when connecting to a database in a SQL Server Availability Group.')

    parser.add_argument(
        u'-M', u'--multi-subnet-failover',
        dest=u'multi_subnet_failover',
        action=u'store_true',
        default=False,
        help=u'If application is connecting to AlwaysOn AG on different subnets, setting this provides faster '
             u'detection and connection to currently active server.')

    parser.add_argument(
        u'-a', u'--packet-size',
        dest=u'packet_size',
        default=0,
        metavar=u'',
        help=u'Size in bytes of the network packets used to communicate with SQL Server.')

    parser.add_argument(
        u'-A', u'--dac-connection',
        dest=u'dac_connection',
        action=u'store_true',
        default=False,
        help=u'Connect to SQL Server using the dedicated administrator connection.')

    parser.add_argument(
        u'--enable-sqltoolsservice-logging',
        dest=u'enable_sqltoolsservice_logging',
        action=u'store_true',
        default=False,
        help=u'Enables diagnostic logging for the SqlToolsService.')

    parser.add_argument(
        u'--prompt',
        dest=u'prompt',
        metavar=u'',
        help=u'Prompt format (Default: \\d> ')

    return parser


parser = initialize()


def parse(args):
    options = parser.parse_args(args)
    return options
