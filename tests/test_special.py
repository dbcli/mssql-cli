import unittest
import uuid
from mssqlutils import create_mssql_cli_client, shutdown
from mssqlcli.packages.special.main import special_command, execute, NO_QUERY


# All tests require a live connection to a SQL Server database
class SpecialCommandsTests(unittest.TestCase):
    session_guid = str(uuid.uuid4().hex)
    table1 = 'mssql_cli_table1_{0}'.format(session_guid)
    table2 = 'mssql_cli_table2_{0}'.format(session_guid)
    view = 'mssql_cli_view_{0}'.format(session_guid)
    database = 'mssql_cli_db_{0}'.format(session_guid)
    schema = 'mssql_cli_schema_{0}'.format(session_guid)
    index = 'mssql_cli_index_{0}'.format(session_guid)

    @classmethod
    def setUpClass(cls):
        try:
            # create the database objects to test upon
            client = create_mssql_cli_client()
            list(client.execute_single_batch_query('CREATE DATABASE {0};'.format(cls.database)))
            list(client.execute_single_batch_query('CREATE TABLE {0} (a int, b varchar(25));'.format(cls.table1)))
            list(client.execute_single_batch_query('CREATE TABLE {0} (x int, y varchar(25), z bit);'.format(cls.table2)))
            list(client.execute_single_batch_query('CREATE VIEW {0} as SELECT a from {1};'.format(cls.view, cls.table1)))
            list(client.execute_single_batch_query('CREATE SCHEMA {0};'.format(cls.schema)))
            list(client.execute_single_batch_query('CREATE INDEX {0} ON {1} (x);'.format(cls.index, cls.table2)))
        finally:
            shutdown(client)

    @classmethod
    def tearDownClass(cls):
        try:
            # delete the database objects created
            client = create_mssql_cli_client()
            list(client.execute_single_batch_query('DROP DATABASE {0};'.format(cls.database)))
            list(client.execute_single_batch_query('DROP INDEX {0} ON {1};'.format(cls.index, cls.table2)))
            list(client.execute_single_batch_query('DROP TABLE {0};'.format(cls.table1)))
            list(client.execute_single_batch_query('DROP TABLE {0};'.format(cls.table2)))
            list(client.execute_single_batch_query('DROP VIEW {0} IF EXISTS;'.format(cls.view)))
            list(client.execute_single_batch_query('DROP SCHEMA {0};'.format(cls.schema)))
        finally:
            shutdown(client)

    def test_list_tables_command(self):
        self.command('\\dt', self.table1, min_rows_expected=2, rows_expected_pattern_query=1, cols_expected=2,
                     cols_expected_verbose=4)

    def test_list_views_command(self):
        self.command('\\dv', self.view, min_rows_expected=1, rows_expected_pattern_query=1, cols_expected=2,
                     cols_expected_verbose=3)

    def test_list_schemas_command(self):
        self.command('\\dn', self.schema, min_rows_expected=1, rows_expected_pattern_query=1, cols_expected=1,
                     cols_expected_verbose=3)

    def test_list_indices_command(self):
        self.command('\\di', self.index, min_rows_expected=1, rows_expected_pattern_query=1, cols_expected=3,
                     cols_expected_verbose=5)

    def test_list_databases_command(self):
        self.command('\\l', self.database, min_rows_expected=1, rows_expected_pattern_query=1, cols_expected=1,
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