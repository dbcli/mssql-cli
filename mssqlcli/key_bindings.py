import logging
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.key_binding import KeyBindings
from .filters import has_selected_completion

_logger = logging.getLogger(__name__)


def mssqlcli_bindings(mssql_cli):
    """
    Custom key bindings for mssqlcli.
    """
    key_bindings = KeyBindings()

    @key_bindings.add(u'f2')
    def _(event):
        """
        Enable/Disable SmartCompletion Mode.
        """
        del event       # event is unused
        _logger.debug('Detected F2 key.')
        mssql_cli.completer.smart_completion = not mssql_cli.completer.smart_completion

    @key_bindings.add(u'f3')
    def _(event):
        """
        Enable/Disable Multiline Mode.
        """
        del event       # event is unused
        _logger.debug('Detected F3 key.')
        mssql_cli.multiline = not mssql_cli.multiline

    @key_bindings.add(u'f4')
    def _(event):
        """
        Toggle between Vi and Emacs mode.
        """
        _logger.debug('Detected F4 key.')
        mssql_cli.vi_mode = not mssql_cli.vi_mode
        event.app.editing_mode = EditingMode.VI if mssql_cli.vi_mode else EditingMode.EMACS

    @key_bindings.add(u'tab')
    def _(event):
        """
        Force autocompletion at cursor.
        """
        _logger.debug('Detected <Tab> key.')
        b = event.app.current_buffer
        if b.complete_state:
            b.complete_next()
        else:
            b.start_completion(select_first=True)

    @key_bindings.add(u'c-space')
    def _(event):
        """
        Initialize autocompletion at cursor.

        If the autocompletion menu is not showing, display it with the
        appropriate completions for the context.

        If the menu is showing, select the next completion.
        """
        _logger.debug('Detected <C-Space> key.')

        b = event.app.current_buffer
        if b.complete_state:
            b.complete_next()
        else:
            b.start_completion(select_first=False)

    @key_bindings.add(u'enter', filter=has_selected_completion)
    def _(event):
        """
        Makes the enter key work as the tab key only when showing the menu.
        """
        _logger.debug('Detected enter key.')

        event.current_buffer.complete_state = None
        b = event.app.current_buffer
        b.complete_state = None

    return key_bindings
