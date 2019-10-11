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

# TODO: add -s with pytest_adotpion


class TestNonInteractiveResults:
    """
    Tests non-interactive features.
    """

    file_root = '%s/test_query_results/' % os.path.dirname(os.path.abspath(__file__))
    testdata = [
        ("SELECT * FROM STRING_SPLIT(REPLICATE(CAST('X,' AS VARCHAR(MAX)), 1024), ',')",
         file_root + 'big.txt'),
        ("select 1", file_root + 'small.txt'),
        ("select 1; select 2;", file_root + 'multiple.txt'),
        ("select %s" % ('x' * 250), file_root + 'col_too_wide.txt')
    ]

    # @classmethod
    # def setup_class(cls):
        # cls.test_db = create_test_db()

    # @classmethod
    # def teardown_class(cls):
        # clean_up_test_db(cls.test_db)

    @pytest.mark.parametrize("query_str, file_baseline", testdata)
    def test_query(self, query_str, file_baseline):
        output_query, output_file = self.execute_query_via_subprocess(query_str, file_baseline)
        assert output_query == output_file

    # TODO: test that calling run with interactive_mode off returns error
    # def test_invalid_run(self):
    #     pass

    # HELPER FUNCTIONS

    def execute_query_via_subprocess(self, query_str, file_baseline):
        """ Helper method for running a query with -Q. """
        p = subprocess.Popen("./mssql-cli -Q \"%s\"" % query_str, shell=True, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = p.communicate()[0].decode("utf-8")
        output_baseline = self.get_file_contents(file_baseline)
        return output, output_baseline

    @staticmethod
    def get_file_contents(file_path):
        """ Get expected result from file. """
        try:
            with open(file_path, 'r') as f:
                return f.read()
        except OSError as e:
            raise e


class TestNonInteractiveClosure:
    """
    Ensures that client session has shut down after mssql-cli runs in non-interactive mode.
    """
    testdata = [
        "select 1",
        "gibberish"
    ]

    @classmethod
    def setup_class(cls):
        """
        Instantiate empty mssql_cli
        """
        cls.mssql_cli = None

    def setup_method(self):
        """ Create new mssql-cli instance for each test """
        self.mssql_cli = create_mssql_cli()

    @pytest.mark.parametrize("query_str", testdata)
    def test_session_closure(self, query_str):
        """ Runs unit tests on process closure given a query string. """
        print("\n")
        try:
            self.mssql_cli = create_mssql_cli()
            self.mssql_cli.execute_query(query_str)
        finally:
            self.mssql_cli.shutdown()
            assert self.mssql_cli.mssqlcliclient_main.sql_tools_client.\
                tools_service_process.poll() is not None
