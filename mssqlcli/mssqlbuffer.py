from __future__ import unicode_literals
import re
import sqlparse
from prompt_toolkit.enums import DEFAULT_BUFFER
from prompt_toolkit.filters import Condition
from prompt_toolkit.application import get_app
from .packages.parseutils.utils import is_open_quote


def mssql_is_multiline(mssql_cli):
    @Condition
    def cond():
        doc = get_app().layout.get_buffer_by_name(DEFAULT_BUFFER).document

        if not mssql_cli.multiline:
            return False
        if mssql_cli.multiline_mode == 'safe':
            return True
        return not _multiline_exception(doc.text)

    return cond


def _is_complete(sql):
    # A complete command is an sql statement that ends with a 'GO', unless
    # there's an open quote surrounding it, as is common when writing a
    # CREATE FUNCTION command
    if sql is not None and sql != "":
        # remove comments
        sql = sqlparse.format(sql, strip_comments=True)

        # check for open comments
        # remove all closed quotes to isolate instances of open comments
        sql_no_quotes = re.sub(r'".*?"|\'.*?\'', '', sql)
        is_open_comment = len(re.findall(r'\/\*', sql_no_quotes)) > 0

        # check that 'go' is only token on newline
        lines = sql.split('\n')
        lastline = lines[len(lines) - 1].lower().strip()
        is_valid_go_on_lastline = lastline == 'go'

        # check that 'go' is on last line, not in open quotes, and there's no open
        # comment with closed comments and quotes removed.
        # NOTE: this method fails when GO follows a closing '*/' block comment on the same line,
        # we've taken a dependency with sqlparse
        # (https://github.com/andialbrecht/sqlparse/issues/484)
        return not is_open_quote(sql) and not is_open_comment and is_valid_go_on_lastline

    return False


def _multiline_exception(text):
    text = text.strip()
    return (
        text.startswith('\\') or  # Special Command
        text.endswith(r'\e') or  # Ended with \e which should launch the editor
        _is_complete(text) or  # A complete SQL command
        (text == 'exit') or  # Exit doesn't need semi-colon
        (text == 'quit') or  # Quit doesn't need semi-colon
        (text == ':q') or  # To all the vim fans out there
        (text == '')  # Just a plain enter without any text
    )
