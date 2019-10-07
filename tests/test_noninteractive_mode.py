""" Non-interactive tests. """
import subprocess
import csv
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
    output = p.communicate(b'y\n')[0].decode("utf-8")

    # start to build the output string to compare
    warning = ("The result set has more than 1000 rows.\n" +
               "Do you want to continue? [y/N]: Warning: Output is not to a terminal (fd=1).\n" +
               "Warning: Input is not to a terminal (fd=0).\n")
    boundary = "+---------+\n"
    header_underscore = "|---------|\n"
    output_compare = "%s%s" % (warning, boundary)

    # get expected result from csv
    with open('tests/results_big_query.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader)
        output_compare += "| %s   |\n%s" % (headers[0], header_underscore)

        for row in reader:
            for col in row:
                output_compare += "| %s       |\n" % col

        output_compare += "|         |\n"
        output_compare += boundary
        output_compare += "(1025 rows affected)\n"

    assert output == output_compare

def test_query_output():
    """ Tests if -Q has equal output to execute_query. """
    # -Q test
    query_str = "select 1"
    p = subprocess.Popen("./mssql-cli -Q '%s'" % query_str, shell=True, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output_dashq = p.communicate()[0].decode("utf-8").rstrip('\n')

    # compare with this result
    output_compare = (
        "Warning: Output is not to a terminal (fd=1).\n" +
        "Warning: Input is not to a terminal (fd=0).\n" +
        "+--------------------+\n" +
        "| (No column name)   |\n" +
        "|--------------------|\n" +
        "| 1                  |\n" +
        "+--------------------+\n" +
        "(1 row affected)"
    )
    assert output_compare == output_dashq

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
