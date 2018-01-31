import logging
from collections import namedtuple

from . import export

logger = logging.getLogger(__name__)

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