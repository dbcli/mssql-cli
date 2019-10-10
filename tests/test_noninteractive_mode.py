""" Non-interactive tests. """
import subprocess
from mssqltestutils import (
    create_mssql_cli,
    # create_test_db,
    # clean_up_test_db,
)


class TestNonInteractive:
    """ Tests non-interactive features. """

    file_root = './tests/test_query_results/'

    # @classmethod
    # def setup_class(cls):
    #     cls.test_db = create_test_db()

    # @classmethod
    # def teardown_class(cls):
    #     clean_up_test_db(cls.test_db)


    # TESTS
    def test_session_closure_query_valid(self):
        """ Test session closure for valid query. """
        assert self.is_processed_closed("select 1")

    def test_session_closure_query_invalid(self):
        """ Test session closure for invalid query. """
        assert self.is_processed_closed("asdfasoifjas")

    def test_query_large(self):
        """ Test against query with over 1000 lines. """
        query_str = "SELECT * FROM STRING_SPLIT(REPLICATE(CAST('X,' AS VARCHAR(MAX)), 1024), ',')"
        file_baseline = self.file_root + 'big.txt'
        output_query, output_file = self.is_query_valid(query_str, file_baseline)
        assert output_query == output_file

    def test_query_small(self):
        """ Tests if -Q has equal output to execute_query. """
        query_str = "select 1"
        file_baseline = self.file_root + 'small.txt'
        output_query, output_file = self.is_query_valid(query_str, file_baseline)
        assert output_query == output_file

    def test_query_multiple(self):
        """ Tests two simple queries in one string. """
        query_str = "select 1; select 2;"
        file_baseline = self.file_root + 'multiple.txt'
        output_query, output_file = self.is_query_valid(query_str, file_baseline)
        assert output_query == output_file

    def test_col_too_wide(self):
        """ Tests query where column is too wide. """
        s = 'x' * 250
        query_str = "select %s" % s
        file_baseline = self.file_root + 'col_too_wide.txt'
        output_query, output_file = self.is_query_valid(query_str, file_baseline)
        assert output_query == output_file


    # HELPER FUNCTIONS

    def is_query_valid(self, query_str, file_baseline):
        """ Helper method for running a query with -Q. """
        p = subprocess.Popen("./mssql-cli -Q \"%s\"" % query_str, shell=True, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = p.communicate()[0].decode("utf-8")
        output_baseline = self.get_file_contents(file_baseline)
        return output, output_baseline

    def is_processed_closed(self, query_str):
        """ Runs unit tests on process closure given a query string. """
        print("\n")
        mssql_cli = create_mssql_cli()
        mssql_cli.execute_query(query_str)
        mssql_cli.shutdown()
        return self.is_process_terminated(mssql_cli)

    def is_process_terminated(self, mssql_cli):
        """ Checks if mssql_cli instance has terminated. """
        return mssql_cli.mssqlcliclient_main.sql_tools_client.tools_service_process.poll() \
            is not None

    def get_file_contents(self, file_path):
        """ Get expected result from file. """
        try:
            with open(file_path, 'r') as f:
                return f.read()
        except OSError as e:
            raise e
