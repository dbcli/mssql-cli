# coding=utf-8
from __future__ import unicode_literals
import os
import platform
from mssqlutils import create_mssql_cli_client, shutdown, run_and_return_string_from_formatter

import pytest
try:
    import setproctitle
except ImportError:
    setproctitle = None

from pgcli.main import (
    obfuscate_process_password, format_output, PGCli, OutputSettings
)


@pytest.mark.skipif(platform.system() == 'Windows',
                    reason='Not applicable in windows')
@pytest.mark.skipif(not setproctitle,
                    reason='setproctitle not available')
def test_obfuscate_process_password():
    original_title = setproctitle.getproctitle()

    setproctitle.setproctitle("pgcli user=root password=secret host=localhost")
    obfuscate_process_password()
    title = setproctitle.getproctitle()
    expected = "pgcli user=root password=xxxx host=localhost"
    assert title == expected

    setproctitle.setproctitle("pgcli user=root password=top secret host=localhost")
    obfuscate_process_password()
    title = setproctitle.getproctitle()
    expected = "pgcli user=root password=xxxx host=localhost"
    assert title == expected

    setproctitle.setproctitle("pgcli user=root password=top secret")
    obfuscate_process_password()
    title = setproctitle.getproctitle()
    expected = "pgcli user=root password=xxxx"
    assert title == expected

    setproctitle.setproctitle("pgcli postgres://root:secret@localhost/db")
    obfuscate_process_password()
    title = setproctitle.getproctitle()
    expected = "pgcli postgres://root:xxxx@localhost/db"
    assert title == expected

    setproctitle.setproctitle(original_title)


def test_format_output():
    settings = OutputSettings(table_format='psql', dcmlfmt='d', floatfmt='g')
    results = format_output('Title', [('abc', 'def')], ['head1', 'head2'],
                            'test status', settings)
    expected = [
        'Title',
        '+---------+---------+',
        '| head1   | head2   |',
        '|---------+---------|',
        '| abc     | def     |',
        '+---------+---------+',
        'test status'
    ]
    assert list(results) == expected


# Runs against an AdventureWorks2014 database in SQL Server
def test_format_array_output():
    statement = u"""
    SELECT
        ShiftID, Name
    from
    HumanResources.Shift
    """
    try:
        client = create_mssql_cli_client()
        result = run_and_return_string_from_formatter(client, statement)
        expected = [
            '+-----------+---------+',
            '| ShiftID   | Name    |',
            '|-----------+---------|',
            '| 1         | Day     |',
            '| 2         | Evening |',
            '| 3         | Night   |',
            '+-----------+---------+',
            '(3 rows affected)'
        ]
        assert list(result) == expected
    finally:
        shutdown(client)


# Runs against AdventureWorks2014 database in SQL Server
def test_format_array_output_expanded():
    statement = u"""
    SELECT Name from HumanResources.Shift
    """

    try:
        client = create_mssql_cli_client()
        result = run_and_return_string_from_formatter(client, statement, expanded=True)

        expected = [
            '-[ RECORD 1 ]-------------------------',
            'Name | Day',
            '-[ RECORD 2 ]-------------------------',
            'Name | Evening',
            '-[ RECORD 3 ]-------------------------',
            'Name | Night',
            '(3 rows affected)'
            ]
        assert list(result) == expected
    finally:
        shutdown(client)


def test_format_output_auto_expand():
    settings = OutputSettings(
        table_format='psql', dcmlfmt='d', floatfmt='g', max_width=100)
    table_results = format_output('Title', [('abc', 'def')],
                                  ['head1', 'head2'], 'test status', settings)
    table = [
        'Title',
        '+---------+---------+',
        '| head1   | head2   |',
        '|---------+---------|',
        '| abc     | def     |',
        '+---------+---------+',
        'test status'
    ]
    assert list(table_results) == table
    expanded_results = format_output(
        'Title',
        [('abc', 'def')],
        ['head1', 'head2'],
        'test status',
        settings._replace(max_width=1)
    )
    expanded = [
        'Title',
        '-[ RECORD 1 ]-------------------------',
        'head1 | abc',
        'head2 | def',
        'test status'
    ]
    assert list(expanded_results) == expanded


# Special commands not supported in Mssql-cli as of Public Preview.
# Tracked via github issue.
"""
@dbtest
def test_i_works(tmpdir, executor):
    sqlfile = tmpdir.join("test.sql")
    sqlfile.write("SELECT NOW()")
    rcfile = str(tmpdir.join("rcfile"))
    cli = PGCli(
        pgexecute=executor,
        pgclirc_file=rcfile,
    )
    statement = r"\i {0}".format(sqlfile)
    run(executor, statement, pgspecial=cli.pgspecial)
"""


def test_missing_rc_dir(tmpdir):
    try:
        rcfile = str(tmpdir.join("subdir").join("rcfile"))
        pgcli = PGCli(pgclirc_file=rcfile)
        assert os.path.exists(rcfile)
    finally:
        pgcli.sqltoolsclient.shutdown()