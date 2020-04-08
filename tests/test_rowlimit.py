# pylint: disable=protected-access
import unittest
import pytest
from mssqlcli.mssql_cli import MssqlCli
from mssqlcli.mssqlclioptionsparser import check_positive_int
from mssqltestutils import create_mssql_cli_options

class RowLimitTests(unittest.TestCase):

    DEFAULT_OPTIONS = create_mssql_cli_options()
    DEFAULT = MssqlCli(DEFAULT_OPTIONS).row_limit
    LIMIT = DEFAULT + 1000

    low_count = 1
    over_default = DEFAULT + 1
    over_limit = LIMIT + 1

    def test_default_row_limit(self):
        cli = MssqlCli(self.DEFAULT_OPTIONS)
        stmt = "SELECT * FROM students"
        result = cli._should_show_limit_prompt(stmt, ['row']*self.low_count)
        assert not result

        result = cli._should_show_limit_prompt(stmt, ['row']*self.over_default)
        assert result

    def test_no_limit(self):
        cli_options = create_mssql_cli_options(row_limit=0)
        cli = MssqlCli(cli_options)
        assert cli.row_limit == 0
        stmt = "SELECT * FROM students"

        result = cli._should_show_limit_prompt(stmt, ['row']*self.over_limit)
        assert not result

    def test_row_limit_on_non_select(self):
        cli = MssqlCli(self.DEFAULT_OPTIONS)
        stmt = "UPDATE students set name='Boby'"
        result = cli._should_show_limit_prompt(stmt, None)
        assert not result

        cli_options = create_mssql_cli_options(row_limit=0)
        assert cli_options.row_limit == 0
        cli = MssqlCli(cli_options)
        result = cli._should_show_limit_prompt(stmt, ['row']*self.over_default)
        assert cli.row_limit == 0
        assert not result


class TestRowLimitArgs:
    """
    Tests for valid row-limit arguments.
    """
    # pylint: disable=protected-access

    test_data_valid = [5, 0]
    test_data_invalid = ['string!', -3]

    @staticmethod
    @pytest.mark.parametrize("row_limit", test_data_valid)
    def test_valid_row_limit(row_limit):
        """
        Test valid value types for row limit argument
        """
        assert check_positive_int(row_limit) == row_limit

    @staticmethod
    @pytest.mark.parametrize("row_limit", test_data_invalid)
    def test_invalid_row_limit(row_limit):
        """
        Test invalid value types for row limit argument
        """
        try:
            check_positive_int(row_limit)
        except SystemExit:
            # mssqlcli class calls sys.exit(1) on invalid value
            assert True
        else:
            assert False
