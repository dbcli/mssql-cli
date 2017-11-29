import logging
import threading

from collections import OrderedDict
from .pgcompleter import PGCompleter

logger = logging.getLogger(u'mssqlcli.completion_refresher')


class CompletionRefresher(object):

    refreshers = OrderedDict()

    def __init__(self):
        self._completer_thread = None
        self._restart_refresh = threading.Event()

    def refresh(self, mssqcliclient, callbacks, history=None,
                settings=None):
        """
        Creates a PGCompleter object and populates it with the relevant
        completion suggestions in a background thread.

        mssqlcliclient - used to extract the credentials to connect
                   to the database.
        settings - dict of settings for completer object
        callbacks - A function or a list of functions to call after the thread
                    has completed the refresh. The newly created completion
                    object will be passed in as an argument to each callback.
        """
        if self.is_refreshing():
            self._restart_refresh.set()
            return [(None, None, None, 'Auto-completion refresh restarted.')]
        else:
            self._completer_thread = threading.Thread(
                target=self._bg_refresh,
                args=(mssqcliclient, callbacks, history, settings),
                name='completion_refresh')
            self._completer_thread.setDaemon(True)
            self._completer_thread.start()
            return [(None, None, None,
                     'Auto-completion refresh started in the background.')]

    def is_refreshing(self):
        return self._completer_thread and self._completer_thread.is_alive()

    def _bg_refresh(self, mssqlcliclient, callbacks, history=None,
                    settings=None):
        settings = settings or {}
        completer = PGCompleter(smart_completion=True, settings=settings)

        executor = mssqlcliclient
        executor.connect()
        # If callbacks is a single function then push it into a list.
        if callable(callbacks):
            callbacks = [callbacks]

        while 1:
            for refresher in self.refreshers.values():
                refresher(completer, executor)
                if self._restart_refresh.is_set():
                    self._restart_refresh.clear()
                    break
            else:
                # Break out of while loop if the for loop finishes natually
                # without hitting the break statement.
                break

            # Start over the refresh from the beginning if the for loop hit the
            # break statement.
            continue

        # Load history into pgcompleter so it can learn user preferences
        n_recent = 100
        if history:
            for recent in history[-n_recent:]:
                completer.extend_query_history(recent, is_init=True)

        for callback in callbacks:
            callback(completer)


def refresher(name, refreshers=CompletionRefresher.refreshers):
    """Decorator to populate the dictionary of refreshers with the current
    function.
    """
    def wrapper(wrapped):
        refreshers[name] = wrapped
        return wrapped
    return wrapper


@refresher('schemata')
def refresh_schemata(completer, mssqlcliclient):
    completer.extend_schemata(mssqlcliclient.schemas())


@refresher('tables')
def refresh_tables(completer, mssqlcliclient):
    completer.extend_relations(mssqlcliclient.tables(), kind='tables')
    completer.extend_columns(mssqlcliclient.table_columns(), kind='tables')
    completer.extend_foreignkeys(mssqlcliclient.foreignkeys())


@refresher('views')
def refresh_views(completer, mssqlcliclient):
    completer.extend_relations(mssqlcliclient.views(), kind='views')
    completer.extend_columns(mssqlcliclient.view_columns(), kind='views')


@refresher('databases')
def refresh_databases(completer, mssqlcliclient):
    completer.extend_database_names(mssqlcliclient.databases())


@refresher('types')
def refresh_types(completer, mssqlcliclient):
    completer.extend_datatypes(mssqlcliclient.user_defined_types())


#@refresher('functions')
#def refresh_functions(completer, executor):
#    completer.extend_functions(executor.functions())
