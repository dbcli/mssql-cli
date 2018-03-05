# coding=utf-8
from __future__ import unicode_literals
import os
import tempfile

from time import sleep

from mssqltestutils import (
    create_mssql_cli,
    create_mssql_cli_options,
    create_mssql_cli_client,
    shutdown
)
from mssqlcli.mssql_cli import OutputSettings, MssqlFileHistory


def test_history_file_not_store_credentials():
    # Used by prompt tool kit, verify statements that contain password or secret
    # are not stored by the history file.
    statements = [
        'Create Database Scoped Credential With Password = <secret>',
        'CREATE MASTER KEY WITH SECRET=xyz',
    ]

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file_path = temp_file.name
        file_history = MssqlFileHistory(temp_file_path)

        for statement in statements:
            file_history.append(statement)

    assert len(file_history) == 0


def test_format_output():
    mssqlcli = create_mssql_cli()
    settings = OutputSettings(table_format='psql', dcmlfmt='d', floatfmt='g')
    results = mssqlcli.format_output('Title',
                                     [('abc', 'def')],
                                     ['head1', 'head2'],
                                     'test status',
                                     settings)
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


def test_format_output_live_connection():
    sleep(7)
    statement = u"""
        select 1 as [ShiftID], 'Day' as [Name] UNION ALL
        select 2, N'魚' UNION ALL
        select 3, 'Night'
    """
    try:
        mssqlcli = create_mssql_cli()
        result = run_and_return_string_from_formatter(mssqlcli, statement)
        expected = [
            u'+-----------+--------+',
            u'| ShiftID   | Name   |',
            u'|-----------+--------|',
            u'| 1         | Day    |',
            u'| 2         | 魚     |',
            u'| 3         | Night  |',
            u'+-----------+--------+',
            u'(3 rows affected)'
        ]
        assert list(result) == expected
    finally:
        shutdown(mssqlcli.mssqlcliclient_main)


def test_format_output_expanded_live_connection():
    statement = u"""
        select N'配列' as [Name] UNION ALL
        select 'Evening' UNION ALL
        select 'Night'
    """

    try:
        mssqlcli = create_mssql_cli()
        result = run_and_return_string_from_formatter(mssqlcli, statement, expanded=True)

        expected = [
            '-[ RECORD 1 ]-------------------------',
            'Name | 配列',
            '-[ RECORD 2 ]-------------------------',
            'Name | Evening',
            '-[ RECORD 3 ]-------------------------',
            'Name | Night',
            '(3 rows affected)'
            ]
        assert list(result) == expected
    finally:
        shutdown(mssqlcli.mssqlcliclient_main)


def test_format_output_auto_expand():
    mssqlcli = create_mssql_cli()
    settings = OutputSettings(
        table_format='psql',
        dcmlfmt='d',
        floatfmt='g',
        max_width=100)
    table_results = mssqlcli.format_output('Title',
                                           [('abc', 'def')],
                                           ['head1', 'head2'],
                                           'test status',
                                           settings)
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
    expanded_results = mssqlcli.format_output(
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


def test_missing_rc_dir(tmpdir):
    try:
        rcfile = str(tmpdir.join("subdir").join("rcfile"))
        mssqlcli = create_mssql_cli(mssqlclirc_file=rcfile)
        assert os.path.exists(rcfile)
    finally:
        mssqlcli.sqltoolsclient.shutdown()


def run_and_return_string_from_formatter(mssql_cli, sql, join=False, expanded=False):
    """
    Return string output for the sql to be run.
    """
    mssql_cli.connect_to_database()
    mssql_cli_client = mssql_cli.mssqlcliclient_main
    for rows, col, message, query, is_error in mssql_cli_client.execute_query(sql):
        settings = OutputSettings(table_format='psql',
                                  dcmlfmt='d',
                                  floatfmt='g',
                                  expanded=expanded)
        formatted = mssql_cli.format_output(None, rows, col, message, settings)
        if join:
            formatted = '\n'.join(formatted)

        return formatted
