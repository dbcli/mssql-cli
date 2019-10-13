"""
Non-interactive tests.
"""
import subprocess
import os
import pytest
from mssqltestutils import (
    create_mssql_cli,
    # create_test_db,
    # clean_up_test_db,
)


class TestNonInteractiveResults:
    """
    Tests non-interactive features.
    """

    file_root = '%s/test_query_results/' % os.path.dirname(os.path.abspath(__file__))
    testdata = [
        ("SELECT * FROM STRING_SPLIT(REPLICATE(CAST('X,' AS VARCHAR(MAX)), 1024), ',')",
         '%sbig.txt' % file_root),
        ("SELECT 1", '%ssmall.txt' % file_root),
        ("SELECT 1; SELECT 2;", '%smultiple.txt' % file_root),
        ("SELECT %s" % ('x' * 250), '%scol_too_wide.txt' % file_root),
        ("SELECT REPLICATE(CAST('X,' AS VARCHAR(MAX)), 1024)", '%scol_wide.txt' % file_root)
    ]

    @pytest.mark.parametrize("query_str, file_baseline", testdata)
    def test_query(self, query_str, file_baseline):
        output_query = self.execute_query_via_subprocess(query_str)
        output_baseline = self.get_file_contents(file_baseline)
        assert output_query == output_baseline

    @staticmethod
    def execute_query_via_subprocess(query_str):
        """ Helper method for running a query with -Q. """
        p = subprocess.Popen("./mssql-cli -Q \"%s\"" % query_str, shell=True, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = p.communicate()[0].decode("utf-8")
        return output

    @staticmethod
    def get_file_contents(file_path):
        """ Get expected result from file. """
        try:
            with open(file_path, 'r') as f:
                return f.read()
        except OSError as e:
            raise e


class TestNonInteractiveShutdown:
    """
    Ensures that client session has shut down after mssql-cli runs in non-interactive mode.
    """
    testdata = [
        "select 1",
        "gibberish"
    ]

    def setup_method(self):
        """ Create new mssql-cli instance for each test """
        # pylint: disable=attribute-defined-outside-init
        self.mssql_cli = create_mssql_cli()

    @pytest.mark.parametrize("query_str", testdata)
    def test_shutdown_after_query(self, query_str):
        """ Runs unit tests on process closure given a query string. """
        print("\n")
        try:
            self.mssql_cli.execute_query(query_str)
        finally:
            self.mssql_cli.shutdown()
            assert self.mssql_cli.mssqlcliclient_main.sql_tools_client.\
                tools_service_process.poll() is not None


# TODO
class TestNonInteractiveApi:
    """
    Test API for non-CLI use cases.
    """
    # TODO: test that calling run() on interactive mode raises exception


# TODO
class TestNonInteractiveDbModification:
    """
    Test DB modification in non-interactive mode.
    """
