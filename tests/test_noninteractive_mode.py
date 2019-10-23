"""
Non-interactive tests.
"""
import subprocess
import os
import pytest
from mssqltestutils import create_mssql_cli

_FILE_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_query_results')

class TestNonInteractiveResults:
    """
    Tests non-interactive features.
    """
    testdata = [
        ("SELECT 1", os.path.join(_FILE_ROOT, 'small.txt')),
        ("SELECT 1; SELECT 2;", os.path.join(_FILE_ROOT, 'multiple.txt')),
        ("SELECT %s" % ('x' * 250), os.path.join(_FILE_ROOT, 'col_too_wide.txt')),
        ("SELECT REPLICATE(CAST('X,' AS VARCHAR(MAX)), 1024)",
         os.path.join(_FILE_ROOT, 'col_wide.txt'))
    ]

    @pytest.mark.parametrize("query_str, file_baseline", testdata)
    def test_query(self, query_str, file_baseline):
        output_query = self.execute_query_via_subprocess(query_str)
        output_baseline = self.get_file_contents(file_baseline)
        assert output_query == output_baseline

    def test_long_query(self):
        """ Output large query using Python class instance. """
        query_str = """ALTER DATABASE keep_AdventureWorks2014 SET COMPATIBILITY_LEVEL = 130
                    SELECT * FROM STRING_SPLIT(REPLICATE(CAST('X,' AS VARCHAR(MAX)), 1024), ',')"""
        try:
            mssqlcli = create_mssql_cli(interactive_mode=False)
            output_query = '\n'.join(mssqlcli.execute_query(query_str))
            output_baseline = self.get_file_contents(os.path.join(_FILE_ROOT, 'big.txt'))
            assert output_query == output_baseline
        finally:
            mssqlcli.shutdown()

    @staticmethod
    def test_noninteractive_run():
        """ Test that calling run throws an exception only when interactive_mode is false """
        mssqlcli = create_mssql_cli(interactive_mode=False)
        try:
            mssqlcli.run()
            assert False
        except ValueError:
            assert True
        finally:
            mssqlcli.shutdown()

    @staticmethod
    def execute_query_via_subprocess(query_str):
        """ Helper method for running a query with -Q. """
        p = subprocess.Popen(os.path.join(".", "mssql-cli -Q \"%s\"" % query_str), shell=True,
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        output = p.communicate()[0].decode("utf-8").replace('\r', '')
        return output

    @staticmethod
    def get_file_contents(file_path):
        """ Get expected result from file. """
        try:
            with open(file_path, 'r', ) as f:
                return f.read().replace('\r', '')   # remove string literals needed in python2
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
        print()
        try:
            self.mssql_cli.execute_query(query_str)
        finally:
            self.mssql_cli.shutdown()
            assert self.mssql_cli.mssqlcliclient_main.sql_tools_client.\
                tools_service_process.poll() is not None
