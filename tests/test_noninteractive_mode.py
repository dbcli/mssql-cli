"""
Non-interactive tests.
"""
import subprocess
import os
import pytest
from mssqltestutils import (
    create_mssql_cli,
    random_str
)

_BASELINE_DIR = os.path.dirname(os.path.abspath(__file__))

class TestNonInteractiveResults:
    """
    Tests non-interactive features.
    """
    @staticmethod
    @pytest.fixture()
    def tmp_filepath():
        """ pytest fixture which returns filepath string and removes the file after tests
        complete. """
        fp = os.path.join(_BASELINE_DIR, "test_query_baseline", "%s.txt" % random_str())
        yield fp
        os.remove(fp)

    testdata = [
        ("SELECT 1", 'small.txt'),
        ("SELECT 1; SELECT 2;", 'multiple.txt'),
        ("SELECT %s" % ('x' * 250), 'col_too_wide.txt'),
        ("SELECT REPLICATE(CAST('X,' AS VARCHAR(MAX)), 1024)", 'col_wide.txt')
    ]

    @pytest.mark.parametrize("query_str, test_file", testdata)
    def test_query(self, query_str, test_file):
        """ Tests -Q """
        file_input, file_baseline = self.input_output_paths(test_file)

        output_query = self.execute_query_via_subprocess(query_str)
        output_baseline = self.get_file_contents(file_baseline)

        # test with -Q
        assert output_query == output_baseline
        # test with -i
        # TODO

    @pytest.mark.parametrize("query_str, test_file", testdata)
    def test_output_file(self, query_str, test_file, tmp_filepath):
        """ Tests -o (and ensures file overwrite works) """
        file_baseline = self.input_output_paths(test_file)[1]

        self.execute_query_via_subprocess(query_str, output_file=tmp_filepath)
        output_query = self.get_file_contents(tmp_filepath)
        output_baseline = self.get_file_contents(file_baseline)

        # test with -Q
        assert output_query == output_baseline
        # test with -i
        # TODO

    def test_long_query(self, tmp_filepath):
        """ Output large query using Python class instance. """
        query_str = """ALTER DATABASE keep_AdventureWorks2014 SET COMPATIBILITY_LEVEL = 130
                    SELECT * FROM STRING_SPLIT(REPLICATE(CAST('X,' AS VARCHAR(MAX)), 1024), ',')"""
        try:
            mssqlcli = create_mssql_cli(interactive_mode=False, output_file=tmp_filepath)
            output_query = '\n'.join(mssqlcli.execute_query(query_str))
            file_baseline = self.input_output_paths('big.txt')[1]
            output_baseline = self.get_file_contents(file_baseline)
            assert output_query == output_baseline

            # test output to file
            output_query_from_file = self.get_file_contents(tmp_filepath)
            assert output_query_from_file == output_baseline
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
    def input_output_paths(test_file_suffix):
        """ Returns tuple of file paths for the input an output of a test. """
        i = os.path.join(_BASELINE_DIR, 'test_query_inputs', 'input_%s' % test_file_suffix)
        o = os.path.join(_BASELINE_DIR, 'test_query_baseline', 'baseline_%s' % test_file_suffix)
        return (i, o)

    @staticmethod
    def execute_query_via_subprocess(query_str, output_file=None):
        """ Helper method for running a query with -Q. """
        cli_call = os.path.join(".", "mssql-cli -Q \"%s\"" % query_str)
        if output_file is not None:
            cli_call += " -o %s" % output_file
        p = subprocess.Popen(cli_call, shell=True, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = p.communicate()[0].decode("utf-8").replace('\r', '')
        return output.strip()

    @staticmethod
    def get_file_contents(file_path):
        """ Get expected result from file. """
        try:
            with open(file_path, 'r') as f:
                # remove string literals (needed in python2) and newlines
                return f.read().replace('\r', '').strip()
        except OSError as e:
            raise e


class TestNonInteractiveShutdownQuery:
    """
    Ensures that client session has shut down after mssql-cli runs in non-interactive mode.
    """
    @staticmethod
    @pytest.fixture(scope='function')
    def mssqlcli():
        """ Create new mssql-cli instance for each test """
        return create_mssql_cli(interactive_mode=False)

    testdata = [
        "select 1",
        "gibberish"
    ]

    @staticmethod
    @pytest.mark.parametrize("query_str", testdata)
    def test_shutdown_after_query(query_str, mssqlcli):
        """ Runs unit tests on process closure given a query string. """
        print()
        try:
            mssqlcli.execute_query(query_str)
        finally:
            mssqlcli.shutdown()
            assert mssqlcli.mssqlcliclient_main.sql_tools_client.\
                tools_service_process.poll() is not None

class TestNonInteractiveShutdownOutput:
    """
    Ensures that client session has shut down after mssql-cli runs in non-interactive mode,
    with -o enabled.
    """
    @staticmethod
    @pytest.fixture(scope='function')
    def mssqlcli():
        """ Create new mssql-cli instance for each test """
        output_file = os.path.join(_BASELINE_DIR, 'tmp.txt')
        yield create_mssql_cli(interactive_mode=False, output_file=output_file)
        os.remove(output_file)

    testdata = [
        "select 1",
        "gibberish"
    ]

    @staticmethod
    @pytest.mark.parametrize("query_str", testdata)
    def test_shutdown_after_query(query_str, mssqlcli):
        """ Runs unit tests on process closure given a query string. """
        print()
        try:
            mssqlcli.execute_query(query_str)
        finally:
            mssqlcli.shutdown()
            assert mssqlcli.mssqlcliclient_main.sql_tools_client.\
                tools_service_process.poll() is not None
