""" Non-interactive tests. """
# import pytest
from mssqltestutils import create_mssql_cli

# class NonInteractiveModeTests:
#     """ tests for non-interactive features (i.e. query-and-exit) """
def test_session_closure():
    """ Test session closure. """
    # mssql_cli_options = create_mssql_cli_options(query="select * from t0")
    # mssql_cli_client = create_mssql_cli_client(mssql_cli_options)
    # mssql_cli_client.connect_to_database()
    # assert mssql_cli_client is not None
    # print("KILLED: %s" % mssql_cli_client.sql_tools_client.tools_service_process.poll())
    
    mssql_cli = create_mssql_cli(query="select * from t0")
    mssql_cli.connect_to_database()

    # ensures process is still running before -Q is processed
    assert not is_process_terminated(mssql_cli)
    mssql_cli.run()
    # process should now be terminated
    assert is_process_terminated(mssql_cli)

def test_execute_query():
    """ Tests if -Q has equal output to execute_query. """
    pass

def is_process_terminated(mssql_cli):
    """ Checks if mssql_cli instance has terminated. """
    return mssql_cli.mssqlcliclient_main.sql_tools_client.tools_service_process.poll() is not None
