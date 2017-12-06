# coding=utf-8
from __future__ import unicode_literals
import os
from mssqlutils import create_mssql_cli_client, shutdown, run_and_return_string_from_formatter
from time import sleep
import pytest
from mssqlcli.main import (
    format_output, MssqlCli, OutputSettings
)


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


def test_format_output_live_connection():
    sleep(7)
    statement = u"""
        select 1 as [ShiftID], 'Day' as [Name] UNION ALL
        select 2, N'魚' UNION ALL
        select 3, 'Night'
    """
    try:
        client = create_mssql_cli_client()
        result = run_and_return_string_from_formatter(client, statement)
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
        shutdown(client)


def test_format_output_expanded_live_connection():
    statement = u"""
        select N'配列' as [Name] UNION ALL
        select 'Evening' UNION ALL
        select 'Night'
    """

    try:
        client = create_mssql_cli_client()
        result = run_and_return_string_from_formatter(client, statement, expanded=True)

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


def test_missing_rc_dir(tmpdir):
    try:
        rcfile = str(tmpdir.join("subdir").join("rcfile"))
        mssqlcli = MssqlCli(mssqlclirc_file=rcfile)
        assert os.path.exists(rcfile)
    finally:
        mssqlcli.sqltoolsclient.shutdown()
