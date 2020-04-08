import os
import sys
import pytest
import utility
from mssqlcli.mssql_cli import MssqlCli
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


class TestInteractiveModeRowLimit:
    # pylint: disable=protected-access

    test_data_valid = [5, 0]
    test_data_invalid = ['string!', -3]

    @staticmethod
    @pytest.mark.parametrize("row_limit", test_data_valid)
    def test_valid_row_limit(row_limit):
        """
        Test valid value types for row limit argument
        """
        assert MssqlCli._set_row_limit(row_limit) == row_limit

    @staticmethod
    @pytest.mark.parametrize("row_limit", test_data_invalid)
    def test_invalid_row_limit(row_limit):
        """
        Test invalid value types for row limit argument
        """
        try:
            MssqlCli._set_row_limit(row_limit)
        except SystemExit:
            # mssqlcli class calls sys.exit(1) on invalid value
            assert True
        else:
            assert False

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
        except SystemExit:
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
        """
        Defaults to environment variable with no config value for pager
        """
        os.environ['PAGER'] = 'testing environ value'

        config = create_mssql_cli_config()

        # remove config pager value if exists
        if 'pager' in config['main'].keys():
            config['main'].pop('pager')

        assert mssqlcli.set_default_pager(config) == 'testing environ value'

        os.environ['PAGER'] = 'less -SRXF'
        assert mssqlcli.set_default_pager(config) == 'less -SRXF'

    @staticmethod
    @pytest.mark.timeout(60)
    def test_pager_config(mssqlcli):
        """
        Defaults to config value over environment variable
        """
        os.environ['PAGER'] = 'less -SRXF'
        config_value = 'testing config value'

        config = create_mssql_cli_config()
        config['main']['pager'] = config_value
        assert mssqlcli.set_default_pager(config) == config_value


class TestInteractiveModeRun:
    """
    Tests the executable.
    """

    @staticmethod
    @pytest.mark.timeout(60)
    def test_valid_command():
        """
        Checks valid command by running mssql-cli executable in repo
        """
        if sys.platform == 'win32':
            exe_name = 'mssql-cli.bat'
        else:
            exe_name = 'mssql-cli'

        assert is_command_valid([os.path.join(utility.ROOT_DIR, exe_name), '--version'])

    @staticmethod
    @pytest.mark.timeout(60)
    def test_invalid_command():
        assert not is_command_valid(None)
        assert not is_command_valid('')
