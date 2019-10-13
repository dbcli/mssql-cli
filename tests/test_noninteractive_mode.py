"""
Non-interactive tests.
"""
import subprocess
import os
import pytest
from mssqltestutils import (
    create_mssql_cli,
    create_test_db,
    clean_up_test_db,
)

_FILE_ROOT = '%s/test_query_results/' % os.path.dirname(os.path.abspath(__file__))

class TestNonInteractiveResults:
    """
    Tests non-interactive features.
    """

    testdata = [
        ("SELECT * FROM STRING_SPLIT(REPLICATE(CAST('X,' AS VARCHAR(MAX)), 1024), ',')",
         '%sbig.txt' % _FILE_ROOT),
        ("SELECT 1", '%ssmall.txt' % _FILE_ROOT),
        ("SELECT 1; SELECT 2;", '%smultiple.txt' % _FILE_ROOT),
        ("SELECT %s" % ('x' * 250), '%scol_too_wide.txt' % _FILE_ROOT),
        ("SELECT REPLICATE(CAST('X,' AS VARCHAR(MAX)), 1024)", '%scol_wide.txt' % _FILE_ROOT)
    ]

    @pytest.mark.parametrize("query_str, file_baseline", testdata)
    def test_query(self, query_str, file_baseline):
        output_query = self.execute_query_via_subprocess(query_str)
        output_baseline = self.get_file_contents(file_baseline)
        assert output_query == output_baseline

    @staticmethod
    def test_noninteractive_run():
        """ Test that calling run throws an exception only when interactive_mode is false """
        mssqlcli = create_mssql_cli(interactive_mode=False)
        try:
            mssqlcli.run()
            mssqlcli.shutdown()
            assert False
        except ValueError:
            assert True
        finally:
            mssqlcli.shutdown()

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


class TestNonInteractiveDbModification:
    """
    Test DB modification in non-interactive mode.
    """

    @staticmethod
    @pytest.fixture(scope="class")
    def test_db():
        """ pytest fixture that creates test db """
        test_db = create_test_db()
        yield test_db
        clean_up_test_db(test_db)

    @staticmethod
    @pytest.fixture(scope="function")
    def mssqlcli(test_db):
        return create_mssql_cli(interactive_mode=False, database=test_db)

    """
    TODO: TESTS TO CONSIDER:
    create table
    modify table name
    modify column
    add column
    delete column
    delete table
"""

    @staticmethod
    def test_create_table(test_db, mssqlcli):
        """ Tests expected result for query. """
        output = str(mssqlcli.execute_query("CREATE TABLE %s (test_col_int int)" % test_db))
        assert output == "['Commands completed successfully.']"

    @staticmethod
    def test_drop_table(test_db, mssqlcli):
        """ Tests expected result for query. """
        output = str(mssqlcli.execute_query("DROP TABLE %s" % test_db))
        assert output == "['Commands completed successfully.']"


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
