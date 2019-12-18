import pytest
from mssqltestutils import (
    create_mssql_cli,
    shutdown,
    test_queries,
    get_file_contents,
    get_io_paths
)

class TestInteractiveModeQueries:
    @staticmethod
    @pytest.fixture(scope='class')
    def mssqlcli():
        """
        Pytest fixture which returns interactive mssql-cli instance
        and cleans up on teardown.
        """
        mssqlcli = create_mssql_cli(interactive_mode=True)
        yield mssqlcli
        shutdown(mssqlcli)

    @staticmethod
    @pytest.mark.parametrize("query_str, test_file", test_queries)
    @pytest.mark.timeout(60)
    def test_query(query_str, test_file, mssqlcli):
        _, file_baseline = get_io_paths(test_file)
        output_baseline = get_file_contents(file_baseline)
        output_query = '\n'.join(mssqlcli.execute_query(query_str))
        assert output_query == output_baseline

class TestInteractiveModeInvalidRuns:
    @pytest.mark.timeout(60)
    def test_noninteractive_run(self):
        '''
        Test that calling run throws an exception only when interactive_mode is false
        '''
        self.invalid_run(interactive_mode=False)

    def test_interactive_output(self):
        '''
        Test run with interactive mode enabled with output file, which should return ValueError
        '''
        self.invalid_run(output_file='will-fail.txt')

    @staticmethod
    @pytest.mark.timeout(60)
    def invalid_run(**options):
        '''
        Tests mssql-cli runs with invalid combination of properities set
        '''
        mssqlcli = None
        try:
            mssqlcli = create_mssql_cli(**options)
            mssqlcli.run()
            assert False
        except ValueError:
            assert True
        finally:
            if mssqlcli is not None:
                shutdown(mssqlcli)
