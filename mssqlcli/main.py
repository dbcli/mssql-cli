from __future__ import unicode_literals
from __future__ import print_function

import os
import sys
import traceback
import logging
import threading
import functools
import humanize
import datetime as dt
import itertools
from time import time
from codecs import open
import platform

from cli_helpers.tabular_output import TabularOutputFormatter
from cli_helpers.tabular_output.preprocessors import (align_decimals,
                                                      format_numbers)
import click
from prompt_toolkit import CommandLineInterface, Application, AbortAction
from prompt_toolkit.enums import DEFAULT_BUFFER, EditingMode
from prompt_toolkit.shortcuts import create_prompt_layout, create_eventloop
from prompt_toolkit.buffer import AcceptAction
from prompt_toolkit.document import Document
from prompt_toolkit.filters import Always, HasFocus, IsDone
from prompt_toolkit.layout.lexers import PygmentsLexer
from prompt_toolkit.layout.processors import (
    ConditionalProcessor, HighlightMatchingBracketProcessor)
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from pygments.lexers.sql import PostgresLexer
from pygments.token import Token

from .mssqlcompleter import MssqlCompleter
from .mssqltoolbar import create_toolbar_tokens_func
from .mssqlstyle import style_factory
from .mssqlbuffer import MssqlBuffer
from .completion_refresher import CompletionRefresher
from .config import (
    get_casing_file,
    config_location,
    ensure_dir_exists,
    get_config)
from .key_bindings import mssqlcli_bindings
from .encodingutils import utf8tounicode
from .encodingutils import text_type
from .__init__ import __version__

click.disable_unicode_literals_warning = True

try:
    from urlparse import urlparse, unquote, parse_qs
except ImportError:
    from urllib.parse import urlparse, unquote, parse_qs
from collections import namedtuple

# mssql-cli imports
from mssqlcli.sqltoolsclient import SqlToolsClient
from mssqlcli.mssqlcliclient import MssqlCliClient, reset_connection_and_clients
import mssqlcli.telemetry as telemetry_session

# Query tuples are used for maintaining history
MetaQuery = namedtuple(
    'Query',
    [
        'query',            # The entire text of the command
        'successful',       # True If all subqueries were successful
        'total_time',       # Time elapsed executing the query
        'meta_changed',     # True if any subquery executed create/alter/drop
        'db_changed',       # True if any subquery changed the database
        'path_changed',     # True if any subquery changed the search path
        'mutated',          # True if any subquery executed insert/update/delete
    ])
MetaQuery.__new__.__defaults__ = ('', False, 0, False, False, False, False)

OutputSettings = namedtuple(
    'OutputSettings',
    'table_format dcmlfmt floatfmt missingval expanded max_width case_function'
)
OutputSettings.__new__.__defaults__ = (
    None, None, None, '<null>', False, None, lambda x: x
)

MSSQLCLI_TELEMETRY_PROMPT = """
Telemetry
---------
By default, mssql-cli collects usage data in order to improve your experience.
The data is anonymous and does not include commandline argument values.
The data is collected by Microsoft.

Disable telemetry collection by setting environment variable MSSQL_CLI_TELEMETRY_OPTOUT to 'True' or '1'.

Microsoft Privacy statement: https://privacy.microsoft.com/en-us/privacystatement
"""


class MssqlCli(object):

    max_len_prompt = 30
    default_prompt = '\\d> '

    def set_default_pager(self, config):
        configured_pager = config['main'].get('pager')
        os_environ_pager = os.environ.get('PAGER')

        if configured_pager:
            self.logger.info(
                'Default pager found in config file: "{}"'.format(configured_pager))
            os.environ['PAGER'] = configured_pager
        elif os_environ_pager:
            self.logger.info('Default pager found in PAGER environment variable: "{}"'.format(
                os_environ_pager))
            os.environ['PAGER'] = os_environ_pager
        else:
            self.logger.info(
                'No default pager found in environment. Using os default pager')

        # Set default set of less recommended options, if they are not already set.
        # They are ignored if pager is different than less.
        if not os.environ.get('LESS'):
            os.environ['LESS'] = '-SRXF'

    # mssql-cli
    def __init__(self, force_passwd_prompt=False,
                 mssqlclirc_file=None, row_limit=None,
                 single_connection=False, less_chatty=None,
                 auto_vertical_output=False, sql_tools_client=None,
                 integrated_auth=False, enable_sqltoolsservice_logging=False,
                 prompt=None):

        self.force_passwd_prompt = force_passwd_prompt

        # Load config.
        c = self.config = get_config(mssqlclirc_file)

        self.logger = logging.getLogger(u'mssqlcli.main')
        self.initialize_logging()

        self.set_default_pager(c)
        self.output_file = None

        self.multi_line = c['main'].as_bool('multi_line')
        self.multiline_mode = c['main'].get('multi_line_mode', 'tsql')
        self.vi_mode = c['main'].as_bool('vi')
        self.auto_expand = auto_vertical_output or c['main']['expand'] == 'auto'
        self.expanded_output = c['main']['expand'] == 'always'
        self.prompt_format = prompt or c['main'].get('prompt', self.default_prompt)
        if row_limit is not None:
            self.row_limit = row_limit
        else:
            self.row_limit = c['main'].as_int('row_limit')

        self.min_num_menu_lines = c['main'].as_int('min_num_menu_lines')
        self.multiline_continuation_char = c['main']['multiline_continuation_char']
        self.table_format = c['main']['table_format']
        self.syntax_style = c['main']['syntax_style']
        self.cli_style = c['colors']
        self.wider_completion_menu = c['main'].as_bool('wider_completion_menu')
        self.less_chatty = bool(
            less_chatty) or c['main'].as_bool('less_chatty')
        self.null_string = c['main'].get('null_string', '<null>')
        self.on_error = c['main']['on_error'].upper()
        self.decimal_format = c['data_formats']['decimal']
        self.float_format = c['data_formats']['float']

        self.now = dt.datetime.today()

        self.completion_refresher = CompletionRefresher()

        self.query_history = []

        keyword_casing = c['main']['keyword_casing']
        self.settings = {
            'casing_file': get_casing_file(c),
            'generate_casing_file': c['main'].as_bool('generate_casing_file'),
            'generate_aliases': c['main'].as_bool('generate_aliases'),
            'asterisk_column_order': c['main']['asterisk_column_order'],
            'qualify_columns': c['main']['qualify_columns'],
            'case_column_headers': c['main'].as_bool('case_column_headers'),
            'search_path_filter': c['main'].as_bool('search_path_filter'),
            'single_connection': single_connection,
            'less_chatty': less_chatty,
            'keyword_casing': keyword_casing,
        }

        completer = MssqlCompleter(settings=self.settings)

        self.completer = completer
        self._completer_lock = threading.Lock()

        self.eventloop = create_eventloop()
        self.cli = None

        # mssql-cli
        self.sqltoolsclient = sql_tools_client if sql_tools_client else SqlToolsClient(
            enable_logging=enable_sqltoolsservice_logging)
        self.mssqlcliclient_query_execution = None
        self.integrated_auth = integrated_auth

    def __del__(self):
        # Shut-down sqltoolsservice
        if self.sqltoolsclient:
            self.sqltoolsclient.shutdown()

    def write_to_file(self, pattern, **_):
        if not pattern:
            self.output_file = None
            message = 'File output disabled'
            return [(None, None, None, message, '', True)]
        filename = os.path.abspath(os.path.expanduser(pattern))
        if not os.path.isfile(filename):
            try:
                open(filename, 'w').close()
            except IOError as e:
                self.output_file = None
                message = str(e) + '\nFile output disabled'
                return [(None, None, None, message, '', False)]
        self.output_file = filename
        message = 'Writing to file "%s"' % self.output_file
        return [(None, None, None, message, '', True)]

    def initialize_logging(self):

        log_file = self.config['main']['log_file']
        if log_file == 'default':
            log_file = config_location() + 'mssqlcli.log'
        ensure_dir_exists(log_file)
        log_level = self.config['main']['log_level']

        # Disable logging if value is NONE by switching to a no-op handler.
        # Set log level to a high value so it doesn't even waste cycles getting
        # called.
        if log_level.upper() == 'NONE':
            handler = logging.NullHandler()
        else:
            handler = logging.FileHandler(os.path.expanduser(log_file))

        level_map = {'CRITICAL': logging.CRITICAL,
                     'ERROR': logging.ERROR,
                     'WARNING': logging.WARNING,
                     'INFO': logging.INFO,
                     'DEBUG': logging.DEBUG,
                     'NONE': logging.CRITICAL
                     }

        log_level = level_map[log_level.upper()]

        formatter = logging.Formatter(
            '%(asctime)s (%(process)d/%(threadName)s) '
            '%(name)s %(levelname)s - %(message)s')

        handler.setFormatter(formatter)

        root_logger = logging.getLogger('mssqlcli')
        root_logger.addHandler(handler)
        root_logger.setLevel(log_level)

        root_logger.info('Initializing mssqlcli logging.')
        root_logger.debug('Log file %r.', log_file)

    def connect(self, database='', server='', user='', port='', passwd='',
                dsn='', encrypt=None, trust_server_certificate=None, connection_timeout=None, application_intent=None,
                multi_subnet_failover=None, packet_size=None, **kwargs):
        # Connect to the database.

        if not user and not self.integrated_auth:
            user = click.prompt(
                'Username (press enter for sa)',
                default=u'sa',
                show_default=False)

        if not server:
            server = u'localhost'

        if not database:
            database = u'master'

        # If password prompt is not forced but no password is provided, try
        # getting it from environment variable.
        if not self.force_passwd_prompt and not passwd:
            passwd = os.environ.get('MSSQL_CLI_PASSWORD', '')

        if not self.integrated_auth:
            # Prompt for a password immediately if requested via the -W flag. This
            # avoids wasting time trying to connect to the database and catching a
            # no-password exception.
            # If we successfully parsed a password from a URI, there's no need to
            # prompt for it, even with the -W flag
            if self.force_passwd_prompt and not passwd:
                passwd = click.prompt('Password', hide_input=True,
                                      show_default=False, type=str)

            if not passwd:
                passwd = click.prompt('Password', hide_input=True,
                                      show_default=False, type=str)

        # Attempt to connect to the database.
        # Note that passwd may be empty on the first attempt. In this case try
        # integrated auth.
        try:
            # mssql-cli
            authentication_type = u'SqlLogin'
            if self.integrated_auth:
                authentication_type = u'Integrated'

            self.mssqlcliclient_query_execution = MssqlCliClient(self.sqltoolsclient, server, user, passwd,
                                                                 database=database,
                                                                 authentication_type=authentication_type,
                                                                 encrypt=encrypt,
                                                                 trust_server_certificate=trust_server_certificate,
                                                                 connection_timeout=connection_timeout,
                                                                 application_intent=application_intent,
                                                                 multi_subnet_failover=multi_subnet_failover,
                                                                 packet_size=packet_size,**kwargs)

            if not self.mssqlcliclient_query_execution.connect():
                click.secho(
                    '\nUnable to connect. Please try again',
                    err=True,
                    fg='red')
                exit(1)

            telemetry_session.set_server_information(
                self.mssqlcliclient_query_execution)

        except Exception as e:  # Connecting to a database could fail.
            self.logger.debug('Database connection failed: %r.', e)
            self.logger.error("traceback: %r", traceback.format_exc())
            click.secho(str(e), err=True, fg='red')
            exit(1)

    def execute_command(self, text, query):
        logger = self.logger

        try:
            output, query = self._evaluate_command(text)
        except KeyboardInterrupt:
            # Issue where Ctrl+C propagates to sql tools service process and kills it,
            # so that query/cancel request can't be sent.
            # Right now the sql_tools_service process is killed and we restart
            # it with a new connection.
            click.secho(u'Cancelling query...', err=True, fg='red')
            reset_connection_and_clients(self.sqltoolsclient,
                                         self.mssqlcliclient_query_execution)
            logger.debug("cancelled query, sql: %r", text)
            click.secho("Query cancelled.", err=True, fg='red')

        except NotImplementedError:
            click.secho('Not Yet Implemented.', fg="yellow")
        except Exception as e:
            logger.error("sql: %r, error: %r", text, e)
            logger.error("traceback: %r", traceback.format_exc())
            click.secho(str(e), err=True, fg='red')
        else:
            try:
                if self.output_file and not text.startswith(('\\o ', '\\? ')):
                    try:
                        with open(self.output_file, 'a', encoding='utf-8') as f:
                            click.echo(text, file=f)
                            click.echo('\n'.join(output), file=f)
                            click.echo('', file=f)  # extra newline
                    except IOError as e:
                        click.secho(str(e), err=True, fg='red')
                else:
                    click.echo_via_pager('\n'.join(output))
            except KeyboardInterrupt:
                pass

            if query.total_time > 1:
                print('Time: %0.03fs (%s)' % (query.total_time,
                                              humanize.time.naturaldelta(query.total_time)))
            else:
                print('Time: %0.03fs' % query.total_time)

            # Check if we need to update completions, in order of most
            # to least drastic changes
            if query.db_changed:
                with self._completer_lock:
                    self.completer.reset_completions()
                self.refresh_completions(persist_priorities='keywords')
            elif query.meta_changed:
                self.refresh_completions(persist_priorities='all')

        return query

    def run_cli(self):
        history_file = self.config['main']['history_file']
        if history_file == 'default':
            history_file = config_location() + 'history'
        history = FileHistory(os.path.expanduser(history_file))

        self.refresh_completions(history=history,
                                 persist_priorities='none')

        self.cli = self._build_cli(history)

        if not self.less_chatty:
            print('Version:', __version__)
            print('Mail: sqlcli@microsoft.com')
            print('Home: http://github.com/dbcli/mssql-cli')

        try:
            while True:
                document = self.cli.run()

                # The reason we check here instead of inside the mssqlcliclient is
                # because we want to raise the Exit exception which will be
                # caught by the try/except block that wraps the mssqlcliclient execute
                # statement.
                if quit_command(document.text):
                    raise EOFError

                # Initialize default metaquery in case execution fails
                query = MetaQuery(query=document.text, successful=False)
                query = self.execute_command(document.text, query)
                self.now = dt.datetime.today()

                # Allow MssqlCompleter to learn user's preferred keywords, etc.

                with self._completer_lock:
                    self.completer.extend_query_history(document.text)

                self.query_history.append(query)

        except EOFError:
            self.mssqlcliclient_query_execution.shutdown()
            if not self.less_chatty:
                print ('Goodbye!')

    def _build_cli(self, history):

        def set_vi_mode(value):
            self.vi_mode = value

        key_binding_manager = mssqlcli_bindings(
            get_vi_mode_enabled=lambda: self.vi_mode,
            set_vi_mode_enabled=set_vi_mode)

        def prompt_tokens(_):
            prompt = self.get_prompt(self.prompt_format)
            return [(Token.Prompt, prompt)]

        def get_continuation_tokens(cli, width):
            continuation = self.multiline_continuation_char * (width - 1) + ' '
            return [(Token.Continuation, continuation)]

        get_toolbar_tokens = create_toolbar_tokens_func(
            lambda: self.vi_mode, None,
            None,
            None)

        layout = create_prompt_layout(
            lexer=PygmentsLexer(PostgresLexer),
            reserve_space_for_menu=self.min_num_menu_lines,
            get_prompt_tokens=prompt_tokens,
            get_continuation_tokens=get_continuation_tokens,
            get_bottom_toolbar_tokens=get_toolbar_tokens,
            display_completions_in_columns=self.wider_completion_menu,
            multiline=True,
            extra_input_processors=[
                # Highlight matching brackets while editing.
                ConditionalProcessor(
                    processor=HighlightMatchingBracketProcessor(
                        chars='[](){}'),
                    filter=HasFocus(DEFAULT_BUFFER) & ~IsDone()),
            ])

        with self._completer_lock:
            buf = MssqlBuffer(
                auto_suggest=AutoSuggestFromHistory(),
                always_multiline=self.multi_line,
                multiline_mode=self.multiline_mode,
                completer=self.completer,
                history=history,
                complete_while_typing=Always(),
                accept_action=AcceptAction.RETURN_DOCUMENT)

            editing_mode = EditingMode.VI if self.vi_mode else EditingMode.EMACS

            application = Application(
                style=style_factory(self.syntax_style, self.cli_style),
                layout=layout,
                buffer=buf,
                key_bindings_registry=key_binding_manager.registry,
                on_exit=AbortAction.RAISE_EXCEPTION,
                on_abort=AbortAction.RETRY,
                ignore_case=True,
                editing_mode=editing_mode)

            cli = CommandLineInterface(application=application,
                                       eventloop=self.eventloop)

            return cli

    def _should_show_limit_prompt(self, status, rows):
        """returns True if limit prompt should be shown, False otherwise."""
        if not rows:
            return False
        return self.row_limit > 0 and len(rows) > self.row_limit

    def _evaluate_command(self, text):
        """Used to run a command entered by the user during CLI operation
        (Puts the E in REPL)

        returns (results, MetaQuery)
        """
        logger = self.logger
        logger.debug('sql: %r', text)

        all_success = True
        meta_changed = False  # CREATE, ALTER, DROP, etc
        mutated = False  # INSERT, DELETE, etc
        db_changed = False
        path_changed = False
        output = []
        total = 0

        # Run the query.
        start = time()

        # mssql-cli
        if not self.mssqlcliclient_query_execution.connect():
            click.secho(u'No connection to server. Exiting.')
            exit(1)

        for rows, columns, status, sql, is_error in self.mssqlcliclient_query_execution.execute_multi_statement_single_batch(
                text):
            total = time() - start
            if self._should_show_limit_prompt(status, rows):
                click.secho('The result set has more than %s rows.'
                            % self.row_limit, fg='red')
                if not click.confirm('Do you want to continue?'):
                    click.secho("Aborted!", err=True, fg='red')
                    break

            if is_error:
                output.append(status)
                all_success = False
                continue

            if self.auto_expand:
                max_width = self.cli.output.get_size().columns
            else:
                max_width = None

            settings = OutputSettings(
                table_format=self.table_format,
                dcmlfmt=self.decimal_format,
                floatfmt=self.float_format,
                missingval=self.null_string,
                expanded=self.expanded_output,
                max_width=max_width,
                case_function=(
                    self.completer.case if self.settings['case_column_headers']
                    else
                    lambda x: x
                )
            )

            formatted = format_output(None, rows, columns, status, settings)
            output.extend(formatted)

            db_changed, new_db_name = has_change_db_cmd(sql, db_changed)
            if new_db_name:
                self.mssqlcliclient_query_execution.database = new_db_name

            if all_success:
                meta_changed = meta_changed or has_meta_cmd(text)

        return output, MetaQuery(
            sql, all_success, total, meta_changed, db_changed, path_changed, mutated)

    def _handle_server_closed_connection(self):
        """Used during CLI execution"""
        reconnect = click.prompt(
            'Connection reset. Reconnect (Y/n)',
            show_default=False, type=bool, default=True)
        if reconnect:
            try:
                reset_connection_and_clients(self.sqltoolsclient,
                                             self.mssqlcliclient_query_execution)

                click.secho('Reconnected!\nTry the command again.', fg='green')
            except Exception as e:
                click.secho(str(e), err=True, fg='red')

    def refresh_completions(self, history=None, persist_priorities='all'):
        """ Refresh outdated completions

        :param history: A prompt_toolkit.history.FileHistory object. Used to
                        load keyword and identifier preferences

        :param persist_priorities: 'all' or 'keywords'
        """

        callback = functools.partial(self._on_completions_refreshed,
                                     persist_priorities=persist_priorities)

        self.completion_refresher.refresh(self.mssqlcliclient_query_execution,
                                          callback, history=history, settings=self.settings)
        return [(None, None, None,
                 'Auto-completion refresh started in the background.')]

    def _on_completions_refreshed(self, new_completer, persist_priorities):
        self._swap_completer_objects(new_completer, persist_priorities)

        if self.cli:
            # After refreshing, redraw the CLI to clear the statusbar
            # "Refreshing completions..." indicator
            self.cli.request_redraw()

    def _swap_completer_objects(self, new_completer, persist_priorities):
        """Swap the completer object in cli with the newly created completer.

            persist_priorities is a string specifying how the old completer's
            learned prioritizer should be transferred to the new completer.

              'none'     - The new prioritizer is left in a new/clean state

              'all'      - The new prioritizer is updated to exactly reflect
                           the old one

              'keywords' - The new prioritizer is updated with old keyword
                           priorities, but not any other.
        """
        with self._completer_lock:
            old_completer = self.completer
            self.completer = new_completer

            if persist_priorities == 'all':
                # Just swap over the entire prioritizer
                new_completer.prioritizer = old_completer.prioritizer
            elif persist_priorities == 'keywords':
                # Swap over the entire prioritizer, but clear name priorities,
                # leaving learned keyword priorities alone
                new_completer.prioritizer = old_completer.prioritizer
                new_completer.prioritizer.clear_names()
            elif persist_priorities == 'none':
                # Leave the new prioritizer as is
                pass

            # When mssql-cli is first launched we call refresh_completions before
            # instantiating the cli object. So it is necessary to check if cli
            # exists before trying the replace the completer object in cli.
            if self.cli:
                self.cli.current_buffer.completer = new_completer

    def get_completions(self, text, cursor_positition):
        with self._completer_lock:
            return self.completer.get_completions(
                Document(text=text, cursor_position=cursor_positition), None)

    def get_prompt(self, string):
        # mssql-cli
        string = string.replace('\\t', self.now.strftime('%x %X'))
        string = string.replace('\\u', self.mssqlcliclient_query_execution.user_name or '(none)')
        string = string.replace('\\h', self.mssqlcliclient_query_execution.prompt_host or '(none)')
        string = string.replace('\\d', self.mssqlcliclient_query_execution.database or '(none)')
        string = string.replace('\\p', str(self.mssqlcliclient_query_execution.prompt_port) or '(none)')
        string = string.replace('\\n', "\n")
        return string

    def get_last_query(self):
        """Get the last query executed or None."""
        return self.query_history[-1][0] if self.query_history else None


@click.command()
@click.option('-S', '--server', default='', envvar='MSSQL_CLI_SERVER',
              help='SQL Server instance name or address.')
@click.option('-U', '--username', 'username', envvar='MSSQL_CLI_USER',
              help='Username to connect to the database.')
@click.option('-W', '--password', 'prompt_passwd', is_flag=True, default=False,
              help='Force password prompt.')
@click.option('-E', '--integrated', 'integrated_auth', is_flag=True, default=False,
              help='Use integrated authentication on windows.')
@click.option('-v', '--version', is_flag=True, help='Version of mssql-cli.')
@click.option('-d', '--database', default='', envvar='MSSQL_CLI_DATABASE',
              help='database name to connect to.')
@click.option('--mssqlclirc', default=config_location() + 'config',
              envvar='MSSQL_CLI_RC', help='Location of mssqlclirc config file.')
@click.option('--row-limit', default=None, envvar='MSSQL_CLI_ROW_LIMIT', type=click.INT,
              help='Set threshold for row limit prompt. Use 0 to disable prompt.')
@click.option('--less-chatty', 'less_chatty', is_flag=True,
              default=False,
              help='Skip intro on startup and goodbye on exit.')
@click.option('--auto-vertical-output', is_flag=True,
              help='Automatically switch to vertical output mode if the result is wider than the terminal width.')
@click.option('-N', '--encrypt', is_flag=True, default=False,
              help='SQL Server uses SSL encryption for all data if the server has a certificate installed.')
@click.option('-C', '--trust-server-certificate', is_flag=True, default=False,
              help='The channel will be encrypted while bypassing walking the certificate chain to validate trust.')
@click.option('-l', '--connect-timeout', default=0, type=int,
              help='Time in seconds to wait for a connection to the server before terminating request.')
@click.option('-K', '--application-intent', default='',
              help='Declares the application workload type when connecting to a database in a SQL Server Availability '
                   'Group.')
@click.option('-M', '--multi-subnet-failover', is_flag=True, default=False,
              help='If application is connecting to AlwaysOn AG on different subnets, setting this provides faster '
                   'detection and connection to currently active server.')
@click.option('-a', '--packet-size', default=0, type=int,
              help='Size in bytes of the network packets used to communicate with SQL Server.')
@click.option('-A', '--dac-connection', is_flag=True, default=False,
              help='Connect to SQL Server using the dedicated administrator connection.')
@click.option('--enable-sqltoolsservice-logging', is_flag=True,
              default=False,
              help='Enables diagnostic logging for the SqlToolsService.')
@click.option('--prompt', help='Prompt format (Default: "{}").'.format(MssqlCli.default_prompt))
def cli(username, server, prompt_passwd, database, version, mssqlclirc, row_limit, less_chatty, auto_vertical_output,
        integrated_auth, encrypt, trust_server_certificate, connect_timeout, application_intent, multi_subnet_failover,
        packet_size, enable_sqltoolsservice_logging, dac_connection, prompt):

    if version:
        print('Version:', __version__)
        sys.exit(0)

    config_dir = os.path.dirname(config_location())
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
        display_telemetry_message()

    if platform.system().lower() != 'windows' and integrated_auth:
        integrated_auth = False
        print (u'Integrated authentication not supported on this platform')

    if dac_connection and server and not server.lower().startswith("admin:"):
        server = "admin:" + server

    mssqlcli = MssqlCli(force_passwd_prompt=prompt_passwd, prompt=prompt, row_limit=row_limit, single_connection=False,
                        mssqlclirc_file=mssqlclirc, less_chatty=less_chatty, auto_vertical_output=auto_vertical_output,
                        integrated_auth=integrated_auth, enable_sqltoolsservice_logging=enable_sqltoolsservice_logging)

    mssqlcli.connect(database, server, username, port='', encrypt=encrypt,
                     trust_server_certificate=trust_server_certificate, connection_timeout=connect_timeout,
                     application_intent=application_intent, multi_subnet_failover=multi_subnet_failover,
                     packet_size=packet_size)

    mssqlcli.logger.debug('Launch Params: \n'
                          '\tdatabase: %r'
                          '\tuser: %r'
                          '\tserver: %r'
                          '\tport: %r', database, username, server, '')

    mssqlcli.run_cli()


def display_telemetry_message():
    print(MSSQLCLI_TELEMETRY_PROMPT)


def has_meta_cmd(query):
    """Determines if the completion needs a refresh by checking if the sql
    statement is an alter, create, drop, commit or rollback."""
    try:
        first_token = query.split()[0]
        if first_token.lower() in ('alter', 'create', 'drop'):
            return True
    except Exception:
        return False

    return False


def has_change_db_cmd(query, db_changed):
    """Determines if the statement is a database switch such as 'use' or '\\c'
       Returns (True, DBName) or (False, None)
    """
    try:
        first_token = query.split()[0]
        if first_token.lower() in ('use', '\\c', '\\connect'):
            return True, query.split()[1].strip('"')
    except Exception:
        return False or db_changed, None

    return False or db_changed, None


def has_change_path_cmd(sql):
    """Determines if the search_path should be refreshed by checking if the
    sql has 'set search_path'."""
    return 'set search_path' in sql.lower()


def is_mutating(status):
    """Determines if the statement is mutating based on the status."""
    if not status:
        return False

    mutating = set(['insert', 'update', 'delete'])
    return status.split(None, 1)[0].lower() in mutating


def quit_command(sql):
    return (sql.strip().lower() == 'exit' or
            sql.strip().lower() == 'quit' or
            sql.strip() == r'\q' or
            sql.strip() == ':q')


def exception_formatter(e):
    return click.style(utf8tounicode(str(e)), fg='red')


def format_output(title, cur, headers, status, settings):
    output = []
    expanded = (settings.expanded or settings.table_format == 'vertical')
    table_format = ('vertical' if settings.expanded else
                    settings.table_format)
    max_width = settings.max_width
    case_function = settings.case_function
    formatter = TabularOutputFormatter(format_name=table_format)

    def format_array(val):
        if val is None:
            return settings.missingval
        if not isinstance(val, list):
            return val
        return '{' + ','.join(text_type(format_array(e)) for e in val) + '}'

    def format_arrays(data, headers, **_):
        data = list(data)
        for row in data:
            row[:] = [
                format_array(val) if isinstance(val, list) else val
                for val in row
            ]

        return data, headers

    output_kwargs = {
        'sep_title': 'RECORD {n}',
        'sep_character': '-',
        'sep_length': (1, 25),
        'missing_value': settings.missingval,
        'integer_format': settings.dcmlfmt,
        'float_format': settings.floatfmt,
        'preprocessors': (format_numbers, format_arrays),
        'disable_numparse': True,
        'preserve_whitespace': True
    }
    if not settings.floatfmt:
        output_kwargs['preprocessors'] = (align_decimals, )

    if title:  # Only print the title if it's not None.
        output.append(title)

    if cur:
        headers = [case_function(utf8tounicode(x)) for x in headers]
        if max_width is not None:
            cur = list(cur)
        formatted = formatter.format_output(cur, headers, **output_kwargs)
        if isinstance(formatted, (text_type)):
            formatted = iter(formatted.splitlines())
        first_line = next(formatted)
        formatted = itertools.chain([first_line], formatted)

        if (not expanded and max_width and len(
                first_line) > max_width and headers):
            formatted = formatter.format_output(
                cur, headers, format_name='vertical', column_types=None, **output_kwargs)
            if isinstance(formatted, (text_type)):
                formatted = iter(formatted.splitlines())

        output = itertools.chain(output, formatted)

    if status:  # Only print the status if it's not None.
        output = itertools.chain(output, [status])

    return output


if __name__ == "__main__":
    try:
        telemetry_session.start()
        cli()
    finally:
        # Upload telemetry async in a separate process.
        telemetry_session.conclude()
