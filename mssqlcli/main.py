from __future__ import unicode_literals
from __future__ import print_function

import getpass
import os
import sys
from builtins import input
import click

from mssqlcli.config import config_location
from mssqlcli.__init__ import __version__
from mssqlcli.mssqlclioptionsparser import create_parser
import mssqlcli.telemetry as telemetry_session

click.disable_unicode_literals_warning = True


MSSQLCLI_TELEMETRY_PROMPT = """
Telemetry
---------
By default, mssql-cli collects usage data in order to improve your experience.
The data is anonymous and does not include commandline argument values.
The data is collected by Microsoft.

Disable telemetry collection by setting environment variable MSSQL_CLI_TELEMETRY_OPTOUT to 'True' or '1'.

Microsoft Privacy statement: https://privacy.microsoft.com/privacystatement
"""


def run_cli_with(options):

    if create_config_dir_for_first_use():
        display_telemetry_message()

    display_version_message(options)

    configure_and_update_options(options)

    # Importing MssqlCli creates a config dir by default.
    # Moved import here so we can create the config dir for first use prior.
    # pylint: disable=import-outside-toplevel
    from mssqlcli.mssql_cli import MssqlCli

    # set interactive mode to false if -Q or -i is specified
    if options.query or options.input_file:
        options.interactive_mode = False

    mssqlcli = MssqlCli(options)
    try:
        mssqlcli.connect_to_database()
        telemetry_session.set_server_information(mssqlcli.mssqlcliclient_main)

        if mssqlcli.interactive_mode:
            mssqlcli.run()
        else:
            text = options.query
            if options.input_file:
                # get query text from input file
                try:
                    with open(options.input_file, 'r') as f:
                        text = f.read()
                except FileNotFoundError as e:
                    click.secho(str(e), err=True, fg='red')
                    sys.exit(1)
            mssqlcli.execute_query(text)
    finally:
        mssqlcli.shutdown()


def configure_and_update_options(options):
    if options.dac_connection and options.server and not \
            options.server.lower().startswith("admin:"):
        options.server = "admin:" + options.server

    if not options.integrated_auth:
        if not options.username:
            options.username = input(u'Username (press enter for sa):') or u'sa'
        if not options.password:
            pw = getpass.getpass()
            if pw is not None:
                pw = pw.replace('\r', '').replace('\n', '')
            options.password = pw


def create_config_dir_for_first_use():
    config_dir = os.path.dirname(config_location())
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
        return True

    return False


def display_version_message(options):
    if options.version:
        print('Version:', __version__)
        sys.exit(0)


def display_telemetry_message():
    print(MSSQLCLI_TELEMETRY_PROMPT)


def main():
    try:
        telemetry_session.start()
        mssqlcli_options_parser = create_parser()
        mssqlcli_options = mssqlcli_options_parser.parse_args(sys.argv[1:])
        run_cli_with(mssqlcli_options)
    finally:
        # Upload telemetry async in a separate process.
        telemetry_session.conclude()


if __name__ == "__main__":
    main()
