""" Non-interactive tests. """
import subprocess
from mssqltestutils import create_mssql_cli

# TESTS

file_root = './tests/test_query_results/'

def test_session_closure_query_valid():
    """ Test session closure for valid query. """
    assert is_processed_closed("select 1")

def test_session_closure_query_invalid():
    """ Test session closure for invalid query. """
    assert is_processed_closed("asdfasoifjas")

def test_query_large():
    """ Test against query with over 1000 lines. """
    query_str = "SELECT * FROM STRING_SPLIT(REPLICATE(CAST('X,' AS VARCHAR(MAX)), 1024), ',')"
    file_baseline = file_root + 'big.txt'
    output_query, output_file = is_query_valid(query_str, file_baseline)
    assert output_query == output_file

def test_query_small():
    """ Tests if -Q has equal output to execute_query. """
    query_str = "select 1"
    file_baseline = file_root + 'small.txt'
    output_query, output_file = is_query_valid(query_str, file_baseline)
    assert output_query == output_file

def test_query_multiple():
    """ Tests two simple queries in one string. """
    query_str = "select 1; select 2;"
    file_baseline = file_root + 'multiple.txt'
    output_query, output_file = is_query_valid(query_str, file_baseline)
    assert output_query == output_file


# HELPER FUNCTIONS

def is_query_valid(query_str, file_baseline):
    """ Helper method for running a query with -Q. """
    p = subprocess.Popen("./mssql-cli -Q \"%s\"" % query_str, shell=True, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = p.communicate()[0].decode("utf-8")
    output_baseline = get_file_contents(file_baseline)
    return output, output_baseline

def is_processed_closed(query_str):
    """ Runs unit tests on process closure given a query string. """
    mssql_cli = create_mssql_cli()
    mssql_cli.execute_query(query_str)
    mssql_cli.shutdown()
    return is_process_terminated(mssql_cli)

def is_process_terminated(mssql_cli):
    """ Checks if mssql_cli instance has terminated. """
    return mssql_cli.mssqlcliclient_main.sql_tools_client.tools_service_process.poll() \
        is not None

def get_file_contents(file_path):
    """ Get expected result from file. """
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except OSError as e:
        raise e
