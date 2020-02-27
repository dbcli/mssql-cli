import os
import pytest
from mssqlcli.util import is_command_valid
from mssqltestutils import (
    create_mssql_cli,
    create_mssql_cli_config,
    shutdown,
    test_queries,
    get_file_contents,
    get_io_paths
)

class TestInteractiveMode:
    """
    Fixture used at class-level.
    """
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

class TestInteractiveModeQueries(TestInteractiveMode):
    @staticmethod
    @pytest.mark.parametrize("query_str, test_file", test_queries)
    @pytest.mark.timeout(60)
    def test_query(query_str, test_file, mssqlcli):
        _, file_baseline = get_io_paths(test_file)
        output_baseline = get_file_contents(file_baseline)
        output_query = '\n'.join(mssqlcli.execute_query(query_str)).replace('\r', '')
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
    def test_output_with_interactive_change():
        '''
        Fails on run after interactive mode has been toggled
        '''
        mssqlcli = create_mssql_cli(interactive_mode=False, output_file='will-fail-eventually.txt')
        mssqlcli.interactive_mode = True
        try:
            mssqlcli.run()
            assert False
        except ValueError:
            assert True
        finally:
            shutdown(mssqlcli)

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

class TestInteractiveModePager(TestInteractiveMode):
    """
    Test default pager setting.
    """

    @staticmethod
    @pytest.mark.timeout(60)
    def test_pager_environ(mssqlcli):
        os.environ['PAGER'] = 'testing environ value'

        config = create_mssql_cli_config()
        assert mssqlcli.set_default_pager(config) == 'testing environ value'

        os.environ['PAGER'] = 'less -SRXF'
        assert mssqlcli.set_default_pager(config) == 'less -SRXF'

    @staticmethod
    @pytest.mark.timeout(60)
    def test_pager_config(mssqlcli):
        # defaults to config value over os.environ
        os.environ['PAGER'] = 'less -SRXF'
        config_value = 'testing config value'

        config = create_mssql_cli_config()
        config['main']['pager'] = config_value
        assert mssqlcli.set_default_pager(config) == config_value

    @staticmethod
    @pytest.mark.timeout(60)
    def test_valid_command():
        assert is_command_valid('cd')

    @staticmethod
    @pytest.mark.timeout(60)
    def test_invalid_command():
        assert not is_command_valid(None)
        assert not is_command_valid('')
