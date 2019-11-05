import unittest
from mssqlcli.mssql_cli import MssqlCli
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
        result = cli._should_show_limit_prompt(['row']*self.low_count)
        assert result is False

        result = cli._should_show_limit_prompt(['row']*self.over_default)
        assert result is True

    def test_no_limit(self):
        cli_options = create_mssql_cli_options(row_limit=0)
        cli = MssqlCli(cli_options)
        assert cli.row_limit is 0
        stmt = "SELECT * FROM students"

        result = cli._should_show_limit_prompt(['row']*self.over_limit)
        assert result is False

    def test_row_limit_on_non_select(self):
        cli = MssqlCli(self.DEFAULT_OPTIONS)
        stmt = "UPDATE students set name='Boby'"
        result = cli._should_show_limit_prompt(None)
        assert result is False

        cli_options = create_mssql_cli_options(row_limit=0)
        assert cli_options.row_limit is 0
        cli = MssqlCli(cli_options)
        result = cli._should_show_limit_prompt(['row']*self.over_default)
        assert cli.row_limit is 0
        assert result is False
