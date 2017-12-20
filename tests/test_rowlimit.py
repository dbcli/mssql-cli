from mssqlcli.main import MssqlCli

DEFAULT = MssqlCli().row_limit
LIMIT = DEFAULT + 1000

low_count = 1
over_default = DEFAULT + 1
over_limit = LIMIT + 1

def test_default_row_limit():
    cli = MssqlCli()
    stmt = "SELECT * FROM students"
    result = cli._should_show_limit_prompt(stmt, ['row']*low_count)
    assert result is False

    result = cli._should_show_limit_prompt(stmt, ['row']*over_default)
    assert result is True


def test_set_row_limit():
    cli = MssqlCli(row_limit=LIMIT)
    stmt = "SELECT * FROM students"
    result = cli._should_show_limit_prompt(stmt, ['row']*over_default)
    assert result is False

    result = cli._should_show_limit_prompt(stmt, ['row']*over_limit)
    assert result is True


def test_no_limit():
    cli = MssqlCli(row_limit=0)
    stmt = "SELECT * FROM students"

    result = cli._should_show_limit_prompt(stmt, ['row']*over_limit)
    assert result is False


def test_row_limit_on_non_select():
    cli = MssqlCli()
    stmt = "UPDATE students set name='Boby'"
    result = cli._should_show_limit_prompt(stmt, None)
    assert result is False

    cli = MssqlCli(row_limit=0)
    result = cli._should_show_limit_prompt(stmt, ['row']*over_default)
    assert result is False
