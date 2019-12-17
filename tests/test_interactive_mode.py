import pytest
from mssqltestutils import (
    create_mssql_cli,
    shutdown,
    test_queries,
    get_file_contents,
    get_io_paths
)

class TestInteractiveMode:
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
