""" Non-interactive tests. """
from mssqltestutils import create_mssql_cli

class TestNonInteractiveMode:
    """ Non-interactive tests. """
    def test_session_closure_query_valid(self):
        """ Test session closure for valid query. """
        assert self.is_processed_closed("select 1")

    def test_session_closure_query_invalid(self):
        """ Test session closure for invalid query. """
        assert self.is_processed_closed("asdfasoifjas")

    def test_execute_query(self):
        """ Tests if -Q has equal output to execute_query. """
        pass

    @classmethod
    def is_processed_closed(cls, query_str):
        """ Runs unit tests on process closure given a query string """
        mssql_cli = create_mssql_cli(query=query_str)
        mssql_cli.connect_to_database()

        # ensures process is still running before -Q is processed
        if cls.is_process_terminated(mssql_cli):
            return False
        mssql_cli.run()
        # process should now be terminated
        return cls.is_process_terminated(mssql_cli)

    @staticmethod
    def is_process_terminated(mssql_cli):
        """ Checks if mssql_cli instance has terminated. """
        return mssql_cli.mssqlcliclient_main.sql_tools_client.tools_service_process.poll() \
            is not None
