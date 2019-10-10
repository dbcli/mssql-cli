""" Non-interactive tests. """
import subprocess
from mssqltestutils import create_mssql_cli

def test_session_closure_query_valid():
    """ Test session closure for valid query. """
    assert is_processed_closed("select 1")

def test_session_closure_query_invalid():
    """ Test session closure for invalid query. """
    assert is_processed_closed("asdfasoifjas")

def test_query_large():
    """ Test against query with over 1000 lines """
    query_str = "SELECT * FROM STRING_SPLIT(REPLICATE(CAST('X,' AS VARCHAR(MAX)), 1024), ',')"
    p = subprocess.Popen("./mssql-cli -Q \"%s\"" % query_str, shell=True, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = p.communicate()[0].decode("utf-8")
    output_baseline = get_file_contents('./tests/query_tests/big_query.txt')
    assert output == output_baseline

def test_query_output():
    """ Tests if -Q has equal output to execute_query. """
    query_str = "select 1"
    p = subprocess.Popen("./mssql-cli -Q '%s'" % query_str, shell=True, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = p.communicate()[0].decode("utf-8").rstrip('\n')
    output_baseline = get_file_contents('./tests/query_tests/small_query.txt')
    assert output == output_baseline

def is_processed_closed(query_str):
    """ Runs unit tests on process closure given a query string """
    mssql_cli = create_mssql_cli()
    mssql_cli.execute_query(query_str)
    mssql_cli.shutdown()
    return is_process_terminated(mssql_cli)

def is_process_terminated(mssql_cli):
    """ Checks if mssql_cli instance has terminated. """
    return mssql_cli.mssqlcliclient_main.sql_tools_client.tools_service_process.poll() \
        is not None

def get_file_contents(file_path):
    """ Get expected result from file """
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except OSError as e:
        raise e
