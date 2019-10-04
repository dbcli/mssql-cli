""" Non-interactive tests. """
from mssqltestutils import create_mssql_cli

def test_session_closure_query_valid():
    """ Test session closure for valid query. """
    assert is_processed_closed("select 1")

def test_session_closure_query_invalid():
    """ Test session closure for invalid query. """
    assert is_processed_closed("asdfasoifjas")

def is_processed_closed(query_str):
    """ Runs unit tests on process closure given a query string """
    mssql_cli = create_mssql_cli(query=query_str)
    mssql_cli.connect_to_database()

    # ensures process is still running before -Q is processed
    if is_process_terminated(mssql_cli):
        return False
    mssql_cli.run()
    # process should now be terminated
    return is_process_terminated(mssql_cli)

def is_process_terminated(mssql_cli):
    """ Checks if mssql_cli instance has terminated. """
    return mssql_cli.mssqlcliclient_main.sql_tools_client.tools_service_process.poll() \
        is not None
