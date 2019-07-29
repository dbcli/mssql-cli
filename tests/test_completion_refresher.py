import time
import unittest
from mock import Mock, patch
from mssqlcli.completion_refresher import CompletionRefresher

class CompletionRefresherTests(unittest.TestCase):

    def test_ctor(self):
        """
        Refresher object should contain a few handlers
        :param refresher:
        :return:
        """
        refresher = CompletionRefresher()
        assert len(refresher.refreshers) > 0
        actual_handlers = set(refresher.refreshers.keys())
        expected_handlers = set(['databases', 'schemas', 'tables', 'types', 'views'])
        assert expected_handlers == actual_handlers

    def test_refresh_called_once(self):
        """

        :param refresher:
        :return:
        """
        callbacks = Mock()
        mssqlcliclient = Mock()
        refresher = CompletionRefresher()

        with patch.object(refresher, '_bg_refresh') as bg_refresh:
            actual = refresher.refresh(mssqlcliclient, callbacks)
            time.sleep(1)  # Wait for the thread to work.
            assert len(actual) == 1
            assert len(actual[0]) == 4
            assert actual[0][3] == 'Auto-completion refresh started in the background.'
            bg_refresh.assert_called_with(mssqlcliclient, callbacks, None, None)

    def test_refresh_called_twice(self):
        """
        If refresh is called a second time, it should be restarted
        :param refresher:
        :return:
        """
        callbacks = Mock()
        mssqlcliclient = Mock()
        refresher = CompletionRefresher()

        def bg_refresh_mock(*args):
            time.sleep(3)  # seconds

        refresher._bg_refresh = bg_refresh_mock

        actual1 = refresher.refresh(mssqlcliclient, callbacks)
        time.sleep(1)  # Wait for the thread to work.
        assert len(actual1) == 1
        assert len(actual1[0]) == 4
        assert actual1[0][3] == 'Auto-completion refresh started in the background.'

        actual2 = refresher.refresh(mssqlcliclient, callbacks)
        time.sleep(1)  # Wait for the thread to work.
        assert len(actual2) == 1
        assert len(actual2[0]) == 4
        assert actual2[0][3] == 'Auto-completion refresh restarted.'

    def test_refresh_with_callbacks(self):
        """
        Callbacks must be called
        :param refresher:
        """
        class MssqlCliClientMock:
            def connect_to_database(self):
                return 'connectionservicetest', []
        
        mssqlcliclient = MssqlCliClientMock()
        callbacks = [Mock()]
        refresher = CompletionRefresher()

        # Set refreshers to 0: we're not testing refresh logic here
        refresher.refreshers = {}
        refresher.refresh(mssqlcliclient, callbacks)
        time.sleep(1)  # Wait for the thread to work.
        assert (callbacks[0].call_count == 1)
