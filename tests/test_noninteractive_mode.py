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
    query_str = "SELECT * FROM STRING_SPLIT(REPLICATE(CAST('X,' AS VARCHAR(MAX)), 1024), ',')"
    p = subprocess.Popen("./mssql-cli -Q \"%s\"" % query_str, shell=True, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = p.communicate()[0].decode("utf-8")
    
    # get expected result from txt
    output_compare = ""
    with open('tests/results_big_query.txt', 'r') as f:
        output_compare = f.read()

    assert output == output_compare

def test_query_output():
    """ Tests if -Q has equal output to execute_query. """
    # -Q test
    query_str = "select 1"
    p = subprocess.Popen("./mssql-cli -Q '%s'" % query_str, shell=True, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output_test = p.communicate()[0].decode("utf-8").rstrip('\n')

    # compare with this result
    output_baseline = (
        "+--------------------+\n" +
        "| (No column name)   |\n" +
        "|--------------------|\n" +
        "| 1                  |\n" +
        "+--------------------+\n" +
        "(1 row affected)"
    )
    assert output_baseline == output_test

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
