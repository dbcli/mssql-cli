# pylint: disable=too-many-arguments

import logging
from collections import namedtuple

from mssqlcli.packages.special import export

logger = logging.getLogger('mssqlcli.special')

NO_QUERY = 0
PARSED_QUERY = 1
RAW_QUERY = 2

SpecialCommand = namedtuple('SpecialCommand',
                            ['handler', 'command', 'shortcut', 'description', 'arg_type', 'hidden',
                             'case_sensitive'])

COMMANDS = {}


@export
class CommandNotFound(Exception):
    pass


@export
def parse_special_command(sql):
    command, _, arg = sql.partition(' ')
    verbose = '+' in command
    command = command.strip().replace('+', '')
    return (command, verbose, arg.strip())


@export
def special_command(command, shortcut, description, arg_type=PARSED_QUERY,
                    hidden=False, case_sensitive=False, aliases=()):
    def wrapper(wrapped):
        register_special_command(wrapped, command, shortcut, description,
                                 arg_type, hidden, case_sensitive, aliases)
        return wrapped
    return wrapper


@export
def register_special_command(handler, command, shortcut, description,
                             arg_type=PARSED_QUERY, hidden=False, case_sensitive=False, aliases=()):
    cmd = command.lower() if not case_sensitive else command
    COMMANDS[cmd] = SpecialCommand(handler, command, shortcut, description,
                                   arg_type, hidden, case_sensitive)
    for alias in aliases:
        cmd = alias.lower() if not case_sensitive else alias
        COMMANDS[cmd] = SpecialCommand(handler, command, shortcut, description,
                                       arg_type, case_sensitive=case_sensitive,
                                       hidden=True)


@export
def execute(mssqlcliclient, sql):
    """Execute a special command and return the results. If the special command
    is not supported a KeyError will be raised.
    """
    command, verbose, pattern = parse_special_command(sql)

    if (command not in COMMANDS) and (command.lower() not in COMMANDS):
        raise CommandNotFound('Command not found: %s' % command)

    try:
        special_cmd = COMMANDS[command]
    except KeyError:
        special_cmd = COMMANDS[command.lower()]
        if special_cmd.case_sensitive:
            raise CommandNotFound('Command not found: %s' % command)

    logger.debug(u'Executing special command %s with argument %s.', command, pattern)

    if special_cmd.arg_type == NO_QUERY:
        return special_cmd.handler()
    if special_cmd.arg_type == PARSED_QUERY:
        return special_cmd.handler(mssqlcliclient=mssqlcliclient, pattern=pattern, verbose=verbose)
    if special_cmd.arg_type == RAW_QUERY:
        return special_cmd.handler(mssqlcliclient=mssqlcliclient, query=sql)

    return None


@special_command('help', '\\?', 'Show this help.', arg_type=NO_QUERY, aliases=('\\?', '?'))
def show_help():  # All the parameters are ignored.
    headers = ['Command', 'Shortcut', 'Description']
    result = []

    for _, value in sorted(COMMANDS.items()):
        if not value.hidden:
            result.append((value.command, value.shortcut, value.description))
    return [(result, headers, None, None, False)]
