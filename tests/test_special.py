import unittest

from mssqlutils import create_mssql_cli_client, shutdown
from mssqlcli.packages.special.main import special_command, execute, NO_QUERY

# All tests require a live connection to a SQL Server database
class SpecialCommandsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            # create the database objects to test upon
            client = create_mssql_cli_client()
            list(client.execute_single_batch_query('CREATE DATABASE testdb1;'))
            list(client.execute_single_batch_query('CREATE TABLE tabletest1 (a int, b varchar(25));'))
            list(client.execute_single_batch_query('CREATE TABLE tabletest2 (x int, y varchar(25), z bit);'))
            list(client.execute_single_batch_query('CREATE VIEW viewtest as SELECT a from tabletest1;'))
            list(client.execute_single_batch_query('CREATE SCHEMA schematest;'))
            list(client.execute_single_batch_query('CREATE INDEX tabletest2index ON tabletest2 (x);'))
        finally:
            shutdown(client)

    @classmethod
    def tearDownClass(cls):
        try:
            # delete the database objects created
            client = create_mssql_cli_client()
            list(client.execute_single_batch_query('DROP DATABASE testdb1;'))
            list(client.execute_single_batch_query('DROP INDEX tabletest2index ON tabletest2;'))
            list(client.execute_single_batch_query('DROP TABLE tabletest1;'))
            list(client.execute_single_batch_query('DROP TABLE tabletest2;'))
            list(client.execute_single_batch_query('DROP VIEW viewtest IF EXISTS;'))
            list(client.execute_single_batch_query('DROP SCHEMA schematest;'))
        finally:
            shutdown(client)

    def test_list_tables_command(self):
        self.command('\\dt', 'tabletest1', min_rows_expected=2, rows_expected_pattern_query=1, cols_expected=2,
                     cols_expected_verbose=4)

    def test_list_views_command(self):
        self.command('\\dv', 'viewtest', min_rows_expected=1, rows_expected_pattern_query=1, cols_expected=2,
                     cols_expected_verbose=3)

    def test_list_schemas_command(self):
        self.command('\\dn', 'schematest', min_rows_expected=1, rows_expected_pattern_query=1, cols_expected=1,
                     cols_expected_verbose=3)

    def test_list_indices_command(self):
        self.command('\\di', 'tabletest2index', min_rows_expected=1, rows_expected_pattern_query=1, cols_expected=3,
                     cols_expected_verbose=5)

    def test_list_databases_command(self):
        self.command('\\l', 'testdb1', min_rows_expected=1, rows_expected_pattern_query=1, cols_expected=1,
                     cols_expected_verbose=4)

    def test_add_new_special_command(self):
        @special_command('\\empty', '\\empty[+]', 'returns an empty list', arg_type=NO_QUERY)
        def empty_list_special_command():
            return []

        ret = execute(None, '\\empty')
        self.assertTrue(len(ret) == 0)

    def command(self, command, pattern, min_rows_expected, rows_expected_pattern_query,
                cols_expected, cols_expected_verbose):
        try:
            client = create_mssql_cli_client()

            for rows, col, message, query, is_error in \
                    client.execute_multi_statement_single_batch(command):
                self.assertTrue(len(rows) >= min_rows_expected)
                self.assertTrue(len(col) == cols_expected)

            # execute with pattern and verbose
            command = command + "+ " + pattern
            for rows, col, message, query, is_error in \
                    client.execute_multi_statement_single_batch(command):
                self.assertTrue(len(rows) == rows_expected_pattern_query)
                self.assertTrue(len(col) == cols_expected_verbose)
        finally:
            shutdown(client)



if __name__ == u'__main__':
    unittest.main()