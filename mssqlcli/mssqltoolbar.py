from __future__ import unicode_literals

from prompt_toolkit.application import get_app
from prompt_toolkit.key_binding.vi_state import InputMode


def _get_vi_mode():
    return {
        InputMode.INSERT: 'I',
        InputMode.NAVIGATION: 'N',
        InputMode.REPLACE: 'R',
        InputMode.INSERT_MULTIPLE: 'M',
    }[get_app().vi_state.input_mode]


def create_toolbar_tokens_func(mssql_cli):
    """
    Return a function that generates the toolbar tokens.
    """
    token = 'class:toolbar'
    token_on = 'class:toolbar.on'
    token_off = 'class:toolbar.off'

    def get_toolbar_tokens():
        result = []
        result.append((token, ' '))

        if mssql_cli.completer.smart_completion:
            result.append((token_on, '[F2] Smart Completion: ON  '))
        else:
            result.append((token_off, '[F2] Smart Completion: OFF  '))

        if mssql_cli.multiline:
            result.append((token_on, '[F3] Multiline: ON  '))
        else:
            result.append((token_off, '[F3] Multiline: OFF  '))

        if mssql_cli.multiline:
            if mssql_cli.multiline_mode == 'safe':
                result.append((token, ' ([Esc] [Enter] to execute]) '))
            else:
                result.append((token, ' ([GO] statement will end the line) '))

        if mssql_cli.vi_mode:
            result.append(
                (token_on, '[F4] Vi-mode (' + _get_vi_mode() + ')'))
        else:
            result.append((token_on, '[F4] Emacs-mode'))

        return result
    return get_toolbar_tokens
