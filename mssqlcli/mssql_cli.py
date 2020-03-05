import datetime as dt
import functools
import itertools
import logging
import os
import sys
import threading
import traceback
# pylint: disable=redefined-builtin
from codecs import open
from collections import namedtuple
from time import time
from cli_helpers.tabular_output import TabularOutputFormatter
from cli_helpers.tabular_output.preprocessors import (align_decimals,
                                                      format_numbers)
import humanize
import click
from prompt_toolkit.shortcuts import PromptSession, CompleteStyle
from prompt_toolkit.completion import DynamicCompleter, ThreadedCompleter
from prompt_toolkit.enums import DEFAULT_BUFFER, EditingMode
from prompt_toolkit.document import Document
from prompt_toolkit.filters import HasFocus, IsDone
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.layout.processors import (ConditionalProcessor,
                                              HighlightMatchingBracketProcessor,
                                              TabsProcessor)
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from pygments.lexers.sql import PostgresLexer
from mssqlcli.config import (
    get_casing_file,
    config_location,
    ensure_dir_exists,
    get_config,
)
from mssqlcli.completion_refresher import CompletionRefresher
from mssqlcli.__init__ import __version__
from mssqlcli.encodingutils import text_type
from mssqlcli.key_bindings import mssqlcli_bindings
from mssqlcli.mssqlcliclient import MssqlCliClient
from mssqlcli.mssqlcompleter import MssqlCompleter
from mssqlcli.mssqlstyle import style_factory, style_factory_output
from mssqlcli.mssqltoolbar import create_toolbar_tokens_func
from mssqlcli.sqltoolsclient import SqlToolsClient
from mssqlcli.packages import special
from mssqlcli.mssqlbuffer import mssql_is_multiline
from mssqlcli.util import is_command_valid
import mssqlcli.localized_strings as localized

# Query tuples are used for maintaining history
MetaQuery = namedtuple(
    'Query',
    [
        'query',                        # The entire text of the command
        'successful',                   # True If all subqueries were successful
        'total_time',                   # Time elapsed executing the query
        'meta_changed',                 # True if any subquery executed create/alter/drop
        'db_changed',                   # True if any subquery changed the database
        'path_changed',                 # True if any subquery changed the search path
        'mutated',                      # True if any subquery executed insert/update/delete
        'contains_secure_statement',    # True if any subquery contains the security statement
    ])
MetaQuery.__new__.__defaults__ = ('', False, 0, False, False, False, False, False)

OutputSettings = namedtuple(
    'OutputSettings',
    'table_format dcmlfmt floatfmt missingval expanded max_width case_function'
)
OutputSettings.__new__.__defaults__ = (
    None, None, None, '<null>', False, None, lambda x: x
)

security_keywords = ['password', 'secret', 'encrypted_value']


def security_words_found_in(query):
    try:
        tokens = query.lower()
        return any([keyword for keyword in security_keywords if keyword in tokens])
    except AttributeError:
        return False


class MssqlFileHistory(FileHistory):
    def append_string(self, string):
        if security_words_found_in(string):
            return

        super(MssqlFileHistory, self).append_string(string)


class MssqlCli(object):
    # pylint: disable=too-many-instance-attributes, useless-object-inheritance

    max_len_prompt = 30
    default_prompt = '\\d> '

    def set_default_pager(self, config):
        configured_pager = config['main'].get('pager')
        os_environ_pager = os.environ.get('PAGER')
        is_less_installed = is_command_valid(['less', '--version'])
        default_pager = configured_pager or os_environ_pager or \
                        ('less -SRXF' if is_less_installed else False) or None

        if configured_pager:
            self.logger.info(
                'Default pager found in config file: "%s"', configured_pager)
        elif os_environ_pager:
            self.logger.info('Default pager found in PAGER environment variable: "%s"',
                             os_environ_pager)
        elif is_less_installed:
            self.logger.info('Default pager set to Less')
        else:
            self.logger.info(
                'No default pager found in environment. Using os default pager')

        # Set default set of less recommended options, if they are not already set.
        # They are ignored if pager is different than less.
        if not os.environ.get('LESS'):
            os.environ['LESS'] = '-SRXF'

        if default_pager is not None:
            os.environ['PAGER'] = default_pager
        return default_pager

    def __init__(self, options):

        # Load config.
        c = self.config = get_config(options.mssqlclirc_file)

        self.initialize_logging()
        self.logger = logging.getLogger(u'mssqlcli.main')

        self.interactive_mode = options.interactive_mode

        self.table_format = c['main']['table_format']
        self.decimal_format = c['data_formats']['decimal']
        self.float_format = c['data_formats']['float']
        self.null_string = c['main'].get('null_string', '<null>')
        self.expanded_output = c['main']['expand'] == 'always'
        self.integrated_auth = options.integrated_auth
        self.less_chatty = bool(
            options.less_chatty) or c['main'].as_bool('less_chatty') or self.interactive_mode

        keyword_casing = c['main']['keyword_casing']
        self.settings = {
            'casing_file': get_casing_file(c),
            'generate_casing_file': c['main'].as_bool('generate_casing_file'),
            'generate_aliases': c['main'].as_bool('generate_aliases'),
            'asterisk_column_order': c['main']['asterisk_column_order'],
            'qualify_columns': c['main']['qualify_columns'],
            'case_column_headers': c['main'].as_bool('case_column_headers'),
            'search_path_filter': c['main'].as_bool('search_path_filter'),
            'single_connection': False,
            'less_chatty': self.less_chatty,
            'keyword_casing': keyword_casing,
        }

        if self.interactive_mode:
            pager = self.set_default_pager(c)
            self.prompt_session = None

            # set auto_expand to false if less is detected with auto expand
            self.auto_expand = options.auto_vertical_output \
                or (c['main']['expand'] == 'auto' and pager != 'less -SRXF')
            self.multiline = c['main'].as_bool('multi_line')
            self.multiline_mode = c['main'].get('multi_line_mode', 'tsql')
            self.vi_mode = c['main'].as_bool('vi')
            self.prompt_format = options.prompt or c['main'].get('prompt', self.default_prompt)
            if options.row_limit is not None:
                self.row_limit = options.row_limit
            else:
                self.row_limit = c['main'].as_int('row_limit')

            self.min_num_menu_lines = c['main'].as_int('min_num_menu_lines')
            self.multiline_continuation_char = c['main']['multiline_continuation_char']
            self.syntax_style = c['main']['syntax_style']
            self.cli_style = c['colors']
            self.output_style = style_factory_output(self.syntax_style, self.cli_style)
            self.wider_completion_menu = c['main'].as_bool('wider_completion_menu')
            self.on_error = c['main']['on_error'].upper()

            self.now = dt.datetime.today()

            self.completion_refresher = CompletionRefresher()

            self.query_history = []

            # Initialize completer
            smart_completion = c['main'].get('smart_completion', 'True').lower() == 'true'
            self.completer = MssqlCompleter(smart_completion=smart_completion,
                                            settings=self.settings)
            self._completer_lock = threading.Lock()

        # input and output file are for non-interactive mode
        self.input_file = options.input_file
        self.output_file = options.output_file

        self.query = options.query

        self.sqltoolsclient = SqlToolsClient(enable_logging=options.enable_sqltoolsservice_logging)
        self.mssqlcliclient_main = MssqlCliClient(options, self.sqltoolsclient)

        # exit and return error if user enters interactive mode with -i or -o arguments enabled
        if self.interactive_mode and (self.input_file or self.output_file):
            raise ValueError("Invalid arguments: -i and -o can only be used in non-interactive "
                             "mode.")

        # exit and return error if both query text and an input file are specified
        if self.query and self.input_file:
            raise ValueError("Invalid arguments: either query [-Q] or input file [-i] may be "
                             "specified.")

    def __del__(self):
        # Shut-down sqltoolsservice
        if self.sqltoolsclient:
            self.sqltoolsclient.shutdown()

    # TODO: possibly use at a later date for expanded output file functionality
    # def write_to_file(self, pattern, **_):
    #     if not pattern:
    #         self.output_file = None
    #         message = 'File output disabled'
    #         return [(None, None, None, message, '', True)]
    #     filename = os.path.abspath(os.path.expanduser(pattern))
    #     if not os.path.isfile(filename):
    #         try:
    #             open(filename, 'w').close()
    #         except IOError as e:
    #             self.output_file = None
    #             message = str(e) + '\nFile output disabled'
    #             return [(None, None, None, message, '', False)]
    #     self.output_file = filename
    #     message = 'Writing to file "%s"' % self.output_file
    #     return [(None, None, None, message, '', True)]

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
            handler = logging.FileHandler(os.path.expanduser(log_file), encoding='utf-8')

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

    def set_main_mssqlcli_client(self, mssqlcli_client):
        self.mssqlcliclient_main = mssqlcli_client

    def connect_to_database(self):
        owner_uri, error_messages = self.mssqlcliclient_main.connect_to_database()
        if not owner_uri and error_messages:
            click.secho('\n'.join(error_messages),
                        err=True,
                        fg='yellow')
            self.logger.debug('Database connection failed: %r.', error_messages)
            sys.exit(1)

    def handle_editor_command(self, text):
        r"""
        Editor command is any query that is prefixed or suffixed
        by a '\e'. The reason for a while loop is because a user
        might edit a query multiple times.
        For eg:
        "select * from \e"<enter> to edit it in vim, then come
        back to the prompt with the edited query "select * from
        blah where q = 'abc'\e" to edit it again.
        :param text: Document
        :return: Document
        """
        # FIXME: using application.pre_run_callables like this here is not the best solution.
        # It's internal api of prompt_toolkit that may change. This was added to fix #668.
        # We may find a better way to do it in the future.
        # pylint: disable=no-member
        editor_command = special.editor_command(text)
        while editor_command:
            filename = special.get_filename(text)
            query = (special.get_editor_query(text) or
                     self.get_last_query())
            sql, message = special.open_external_editor(filename, sql=query)
            if message:
                # Something went wrong. Raise an exception and bail.
                raise RuntimeError(message)
            while True:
                try:
                    text = self.prompt_session.prompt(default=sql)
                    break
                except KeyboardInterrupt:
                    sql = ""

            editor_command = special.editor_command(text)
        return text

    def _execute_interactive_command(self, text):
        """ Runs commands in the interactive CLI mode. """

        logger = self.logger

        # Initialize default metaquery in case execution fails
        query = MetaQuery(query=text, successful=False)

        try:
            output, query = self._evaluate_command(text)
        except KeyboardInterrupt:
            # Issue where Ctrl+C propagates to sql tools service process and kills it,
            # so that query/cancel request can't be sent.
            # Right now the sql_tools_service process is killed and we restart
            # it with a new connection.
            click.secho(u'Cancelling query...', err=True, fg='red')
            self.reset()
            logger.debug("cancelled query, sql: %r", text)
            click.secho("Query cancelled.", err=True, fg='red')

        except NotImplementedError:
            click.secho('Not Yet Implemented.', fg="yellow")
        else:
            if query.total_time > 1:
                # pylint: disable=no-member
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

        if not query.contains_secure_statement:
            # Allow MssqlCompleter to learn user's preferred keywords, etc.
            with self._completer_lock:
                self.completer.extend_query_history(text)

            self.query_history.append(query)

        return output

    def execute_query(self, text):
        """ Processes a query string and outputs to file or terminal """

        text = str(text)
        if self.interactive_mode:
            output = self._execute_interactive_command(text)
        else:
            # non-interactive mode
            output, _ = self._evaluate_command(text)

        self._output_query(output)
        return output

    def _output_query(self, output):
        """ Specifies how query output is handled """
        if self.interactive_mode:
            click.echo_via_pager('\n'.join(output))
        else:
            if self.output_file:
                try:
                    with open(self.output_file, 'w', encoding='utf-8') as f:
                        click.echo('\n'.join(output), file=f)
                except IOError as e:
                    click.secho(str(e), err=True, fg='red')
                    sys.exit(1)
            else:
                click.echo('\n'.join(output))

    def run(self):
        """ Spins up CLI. """

        # raise error if interactive mode is set to false here
        if not self.interactive_mode:
            raise ValueError("Invalid arguments: 'run' must be used in interactive mode! Please set "
                             "interactive_mode to True.")

        # exit and return error if user enters interactive mode with -o argument enabled
        if self.output_file:
            raise ValueError("Invalid arguments: -o must be used with interactive mode set to "
                             "false.")

        history_file = self.config['main']['history_file']
        if history_file == 'default':
            history_file = config_location() + 'history'
        history = MssqlFileHistory(os.path.expanduser(history_file))

        self.refresh_completions(history=history,
                                 persist_priorities='none')

        self.prompt_session = self._build_cli(history)

        if not self.less_chatty:
            print('Version: {}'.format(__version__))
            print('Mail: sqlcli@microsoft.com')
            print('Home: http://github.com/dbcli/mssql-cli')

        try:
            while True:
                try:
                    text = self.prompt_session.prompt()
                except KeyboardInterrupt:
                    continue

                # The reason we check here instead of inside the mssqlcliclient is
                # because we want to raise the Exit exception which will be
                # caught by the try/except block that wraps the mssqlcliclient execute
                # statement.
                if self.quit_command(text):
                    raise EOFError

                try:
                    text = self.handle_editor_command(text)
                except RuntimeError as e:
                    self.logger.error("sql: %r, error: %r", text, e)
                    self.logger.error("traceback: %r", traceback.format_exc())
                    click.secho(str(e), err=True, fg='red')
                    continue

                self.execute_query(text)
                self.now = dt.datetime.today()

        except EOFError:
            self.mssqlcliclient_main.shutdown()
            if not self.less_chatty:
                print(localized.goodbye())

    def _build_cli(self, history):
        """
            Builds prompt session.
            NOTE: PROMPT-SESSION USES THIS AS DEPENDENCY.
        """

        def get_message():
            prompt = self.get_prompt(self.prompt_format)
            return [(u'class:prompt', prompt)]

        def get_continuation(width, line_number, is_soft_wrap):
            """
                NOTE: updating parameters will cause prompt session to crash.
            """
            # pylint: disable=unused-argument
            continuation = self.multiline_continuation_char * (width - 1) + ' '
            return [(u'class:continuation', continuation)]

        get_toolbar_tokens = create_toolbar_tokens_func(self)

        if self.wider_completion_menu:
            complete_style = CompleteStyle.MULTI_COLUMN
        else:
            complete_style = CompleteStyle.COLUMN

        with self._completer_lock:
            self.prompt_session = PromptSession(
                message=get_message,
                style=style_factory(self.syntax_style, self.cli_style),

                # Layout options.
                lexer=PygmentsLexer(PostgresLexer),
                prompt_continuation=get_continuation,
                bottom_toolbar=get_toolbar_tokens,
                complete_style=complete_style,
                input_processors=[
                    ConditionalProcessor(
                        processor=HighlightMatchingBracketProcessor(
                            chars='[](){}'),
                        #pylint: disable=invalid-unary-operand-type
                        filter=HasFocus(DEFAULT_BUFFER) & ~IsDone()),
                    # Render \t as 4 spaces instead of "^I"
                    TabsProcessor(char1=u' ', char2=u' ')],
                reserve_space_for_menu=self.min_num_menu_lines,

                # Buffer options.
                multiline=mssql_is_multiline(self),
                completer=ThreadedCompleter(
                    DynamicCompleter(lambda: self.completer)),
                history=history, auto_suggest=AutoSuggestFromHistory(),
                complete_while_typing=True,

                # Key bindings.
                enable_system_prompt=True,
                enable_open_in_editor=True,

                # Other options.
                key_bindings=mssqlcli_bindings(self),
                editing_mode=EditingMode.VI if self.vi_mode else EditingMode.EMACS,
                search_ignore_case=True)

            return self.prompt_session

    def _should_show_limit_prompt(self, status, rows):
        """
            Returns True if limit prompt should be shown, False otherwise.
            NOTE: updating parameters will cause prompt session to crash.
        """
        # pylint: disable=unused-argument
        if not rows:
            return False
        return self.interactive_mode and self.row_limit > 0 and len(rows) > self.row_limit

    def _evaluate_command(self, text):
        """
            Used to run a command entered by the user during CLI operation
            (Puts the E in REPL)

            returns (results, MetaQuery)
        """
        # pylint: disable=too-many-locals

        all_success = True
        meta_changed = False  # CREATE, ALTER, DROP, etc
        mutated = False  # INSERT, DELETE, etc
        db_changed = False
        contains_secure_statement = False
        path_changed = False
        output = []
        total = 0

        # Run the query.
        start = time()

        # mssql-cli
        if not self.mssqlcliclient_main.connect_to_database():
            click.secho(u'No connection to server. Exiting.')
            sys.exit(1)

        for rows, columns, status, sql, is_error in \
                self.mssqlcliclient_main.execute_query(text):

            total = time() - start
            if self._should_show_limit_prompt(status, rows):
                click.secho('The result set has more than %s rows.'
                            % self.row_limit, fg='red')
                if not click.confirm('Do you want to continue?'):
                    click.secho("Aborted!", err=True, fg='red')
                    break

            contains_secure_statement = security_words_found_in(sql)

            if is_error:
                output.append(status)
                all_success = False
                continue

            if self.interactive_mode and self.auto_expand and self.prompt_session:
                max_width = self.prompt_session.output.get_size().columns
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
                    self.completer.case if self.interactive_mode and
                    self.settings['case_column_headers']
                    else
                    lambda x: x
                )
            )

            formatted = self.format_output(None, rows, columns, status, settings)
            output.extend(formatted)

            db_changed, new_db_name = self.has_change_db_cmd(sql)

            if new_db_name:
                self.logger.info('Database context changed.')
                self.mssqlcliclient_main.connected_database = new_db_name

            if all_success:
                meta_changed = meta_changed or self.has_meta_cmd(text)

        return output, MetaQuery(
            text, all_success, total, meta_changed, db_changed, path_changed, mutated,
            contains_secure_statement)

    def _handle_server_closed_connection(self):
        """Used during CLI execution"""
        reconnect = click.prompt(
            'Connection reset. Reconnect (Y/n)',
            show_default=False, type=bool, default=True)
        if reconnect:
            self.reset()
            click.secho('Reconnected!\nTry the command again.', fg='green')

    def shutdown(self):
        """ API for shutting down client """
        self.mssqlcliclient_main.shutdown()

    def reset(self):
        """
        Reset mssqlcli client with a new sql tools service and connection.
        """
        self.sqltoolsclient.shutdown()
        self.sqltoolsclient = SqlToolsClient()

        self.mssqlcliclient_main = self.mssqlcliclient_main.clone(self.sqltoolsclient)

        database_response = self.mssqlcliclient_main.connect_to_database()
        if not database_response:
            click.secho('Unable reconnect to server %s; database %s.' % (
                self.mssqlcliclient_main.server_name,
                self.mssqlcliclient_main.connected_database),
                        err=True, fg='yellow')

            self.logger.info(u'Unable to reset connection to server %s; database %s',
                             self.mssqlcliclient_main.server_name,
                             self.mssqlcliclient_main.connected_database)

            sys.exit(1)
        else:
            owner_uri, error_messages = database_response
            if not owner_uri and error_messages:
                # can occur if database credentials change during reset
                self.logger.error(u'Error in reset : %s', error_messages)
                raise ConnectionResetError(error_messages)

    def refresh_completions(self, history=None, persist_priorities='all'):
        # Clone mssqlcliclient to create a new connection with a new owner Uri.
        mssqlclclient_completion_refresher = self.mssqlcliclient_main.clone()

        callback = functools.partial(self._on_completions_refreshed,
                                     persist_priorities=persist_priorities)

        self.completion_refresher.refresh(mssqcliclient=mssqlclclient_completion_refresher,
                                          callbacks=callback,
                                          history=history,
                                          settings=self.settings)

        return [(None, None, None,
                 'Auto-completion refresh started in the background.')]

    def _on_completions_refreshed(self, new_completer, persist_priorities):
        self._swap_completer_objects(new_completer, persist_priorities)

        if self.prompt_session:
            # After refreshing, redraw the CLI to clear the statusbar
            # "Refreshing completions..." indicator
            self.prompt_session.app.invalidate()

    def _swap_completer_objects(self, new_completer, persist_priorities):
        """Swap the completer object with the newly created completer.

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

            self.completer = new_completer

    def get_completions(self, text, cursor_position):
        with self._completer_lock:
            return self.completer.get_completions(
                Document(text=text, cursor_position=cursor_position), None)

    def get_prompt(self, string):
        string = string.replace('\\t', self.now.strftime('%x %X'))
        string = string.replace('\\u', self.mssqlcliclient_main.user_name or '(none)')
        string = string.replace('\\h', self.mssqlcliclient_main.prompt_host or '(none)')
        string = string.replace('\\d', self.mssqlcliclient_main.connected_database or '(none)')
        string = string.replace('\\p', str(self.mssqlcliclient_main.prompt_port) or '(none)')
        string = string.replace('\\n', "\n")
        return string

    def get_last_query(self):
        """Get the last query executed or None."""
        return self.query_history[-1][0] if self.query_history else None

    @staticmethod
    def has_meta_cmd(query):
        """Determines if the completion needs a refresh by checking if the sql
        statement is an alter, create, drop, commit or rollback."""
        if query and isinstance(query, str):
            first_token = query.split()[0]
            if first_token.lower() in ('alter', 'create', 'drop'):
                return True
        return False

    @staticmethod
    def has_change_db_cmd(query):
        """Determines if the statement is a database switch such as 'use' or '\\c'
           Returns (True, DBName) or (False, None)
        """
        if query and isinstance(query, str):
            first_token = query.split()[0]
            if first_token.lower() in ('use', '\\c', '\\connect'):
                return True, query.split()[1].strip('"')

        return False, None

    @staticmethod
    def quit_command(sql):
        return (sql.strip().lower() == 'exit' or
                sql.strip().lower() == 'quit' or
                sql.strip() == r'\q' or
                sql.strip() == ':q')

    @staticmethod
    def format_output(title, cur, headers, status, settings):
        # pylint: disable=too-many-locals

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

        if title:
            output.append(title)

        if cur:
            headers = [case_function(x) for x in headers]
            if max_width is not None:
                cur = list(cur)
            formatted = formatter.format_output(cur, headers, **output_kwargs)
            if isinstance(formatted, text_type):
                formatted = iter(formatted.splitlines())
            first_line = next(formatted)
            formatted = itertools.chain([first_line], formatted)

            if (not expanded and max_width and len(
                    first_line) > max_width and headers):
                formatted = formatter.format_output(
                    cur, headers, format_name='vertical', column_types=None, **output_kwargs)
                if isinstance(formatted, text_type):
                    formatted = iter(formatted.splitlines())

            output = itertools.chain(output, formatted)

        if status:  # Only print the status if it's not None.
            output = itertools.chain(output, [status])

        return output
