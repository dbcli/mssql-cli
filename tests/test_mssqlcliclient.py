# coding=utf-8
import os
import io
import unittest
import mssqlcli.sqltoolsclient as sqltoolsclient
from utility import random_str

from mssqlcli.jsonrpc.jsonrpcclient import JsonRpcWriter
from mssqltestutils import (
    create_mssql_cli,
    create_mssql_cli_options,
    create_mssql_cli_client,
    shutdown
)
from time import sleep


# All tests apart from test_mssqlcliclient_request_response require a live connection to an
# AdventureWorks2014 database with a hardcoded test server.
# Make modifications to mssqlutils.create_mssql_cli_client() to use a different server and database.
# Please Note: These tests cannot be run offline.
class MssqlCliClientTests(unittest.TestCase):
    """
        Tests for mssqlcliclient.py and sqltoolsclient.py.
    """
    def test_mssqlcliclient_request_response(self):
        """
        Test mssqlcliclient pipeline for sending request and receiving response works.
        """

        def get_test_baseline(file_name):
            """
            Helper method to get baseline file.
            """
            return os.path.abspath(
                os.path.join(
                    os.path.abspath(__file__),
                    u'..',
                    u'..',
                    u'mssqlcli',
                    u'jsonrpc',
                    u'contracts',
                    u'tests',
                    u'baselines',
                    file_name))

        with open(get_test_baseline(u'test_simple_query.txt'), u'r+b', buffering=0) as response_file:
            request_stream = io.BytesIO()
            self.sql_tools_client = sqltoolsclient.SqlToolsClient(
                input_stream=request_stream, output_stream=response_file)

            # The sleep is required because py.test and logging have an issue with closing the FileHandle
            # in a non-thread safe way
            # issue24262
            sleep(0.5)

        self.mssql_cli_options = create_mssql_cli_options(integrated_auth=True)
        self.mssql_cli_client = create_mssql_cli_client(self.mssql_cli_options,
                                                        owner_uri=u'connectionservicetest',
                                                        sql_tools_client=self.sql_tools_client,
                                                        extra_bool_param=True,
                                                        extra_string_param=u'stringparam',
                                                        extra_int_param=5)

        self.mssql_cli_client.shutdown()

    def test_connection(self):
        """
            Verify a successful connection via returned owner uri.
        """
        try:
            client = create_mssql_cli_client(owner_uri=u'connectionservicetest')

            self.assertEqual(client.owner_uri, u'connectionservicetest')
        finally:
            shutdown(client)

    def test_get_query_results(self):
        """
            Verify number of rows returned and returned query.
        """
        try:
            client = create_mssql_cli_client()
            test_query = u"""
                select 1 as [ShiftID], 'Day' as [Name] UNION ALL
                select 2, N'魚' UNION ALL
                select 3, 'Night'
            """

            for rows, col, message, query, is_error in client.execute_query(test_query):
                self.assertTrue(len(rows), 3)
                self.assertTrue(query, test_query)
        finally:
            shutdown(client)

    def test_json_writer_extra_params(self):
        """
            Verify JSON RPC accepts extra paramaters.
        """
        try:
            client = create_mssql_cli_client()
            extra_params = client.extra_params
            json_writer = JsonRpcWriter(io.BytesIO())
            json_writer.send_request(u'test/method', extra_params, id=1)
        except Exception as ex:
            self.fail(u'Exception from JsonRpcWriter %s' % ex)
        finally:
            json_writer.close()
            shutdown(client)

    def test_schema_table_views_and_columns_query(self):
        """
            Verify mssqlcliclient's tables, views, columns, and schema are populated.
            Note: This test should run against a database that the credentials
                  MSSQL_CLI_USER and MSSQL_CLI_PASSWORD have write access to.
        """
        try:
            client = create_mssql_cli_client()
            list(client.execute_query('CREATE TABLE tabletest1 (a int, b varchar(25));'))
            list(client.execute_query('CREATE TABLE tabletest2 (x int, y varchar(25), z bit);'))
            list(client.execute_query('CREATE VIEW viewtest as SELECT a from tabletest1;'))
            list(client.execute_query('CREATE SCHEMA schematest;'))
            list(client.execute_query('CREATE TABLE schematest.tabletest1 (a int);'))

            assert ('schematest', 'tabletest1') in set(client.get_tables())
            assert ('dbo', 'viewtest') in set(client.get_views())
            assert ('schematest', 'tabletest1', 'a', 'int', 'NULL') in set(client.get_table_columns())
            assert ('dbo', 'viewtest', 'a', 'int', 'NULL') in set(client.get_view_columns())
            assert 'schematest' in client.get_schemas()

        finally:
            list(client.execute_query('DROP TABLE tabletest1;'))
            list(client.execute_query('DROP TABLE tabletest2;'))
            list(client.execute_query('DROP VIEW viewtest IF EXISTS;'))
            list(client.execute_query('DROP TABLE schematest.tabletest1;'))
            list(client.execute_query('DROP SCHEMA schematest;'))
            shutdown(client)

    def test_mssqlcliclient_reset_connection(self):
        """
            Verify if the MssqlCliClient can successfully reset its connection
        """
        try:
            mssqlcli = create_mssql_cli()
            mssqlcli.reset()
        finally:
            shutdown(mssqlcli.mssqlcliclient_main)

    def test_mssqlcliclient_multiple_statement(self):
        """
            Verify correct execution of queries separated by semi-colon
        """
        try:
            client = create_mssql_cli_client()
            multi_statement_query = u"select 'Morning' as [Name] UNION ALL select 'Evening'; select 1;"
            multi_statement_query2 = u"select 1; select 'foo' from teapot;"
            multi_statement_query3 = u"select 'foo' from teapot; select 2;"
            for rows, col, message, query, is_error in client.execute_query(multi_statement_query):
                if query == u"select 'Morning' as [Name] UNION ALL select 'Evening'":
                    self.assertTrue(len(rows), 2)
                else:
                    self.assertTrue(len(rows), 1)

            for rows, col, message, query, is_error in \
                    client.execute_query(multi_statement_query2):
                if query == u"select 1":
                    self.assertTrue(len(rows) == 1)
                else:
                    self.assertTrue(is_error)

            for rows, col, message, query, is_error in \
                    client.execute_query(multi_statement_query3):
                if query == u"select 2":
                    self.assertTrue(len(rows) == 1)
                else:
                    self.assertTrue(is_error)

        finally:
            shutdown(client)

    def test_stored_proc_multiple_result_sets(self):
        """
            Verify the results of running a stored proc with multiple result sets
        """
        try:
            client = create_mssql_cli_client()
            create_stored_proc = u"CREATE PROC sp_mssqlcli_multiple_results " \
                          u"AS " \
                          u"BEGIN " \
                          u"SELECT 'Morning' as [Name] UNION ALL select 'Evening' " \
                          u"SELECT 'Dawn' as [Name] UNION ALL select 'Dusk' UNION ALL select 'Midnight' " \
                          u"END"
            exec_stored_proc = u"EXEC sp_mssqlcli_multiple_results"
            del_stored_proc = u"DROP PROCEDURE sp_mssqlcli_multiple_results"

            list(client.execute_query(create_stored_proc))
            row_counts = []
            for rows, columns, message, query, is_error in client.execute_query(exec_stored_proc):
                row_counts.append(len(rows))
            self.assertTrue(row_counts[0] == 2)
            self.assertTrue(row_counts[1] == 3)
            list(client.execute_query(del_stored_proc))
        finally:
            shutdown(client)

    
    def test_select_result_unicode_encoded(self):
        """
            Verify the column names and string values in rows returned by select statement are properly encoded as unicode.
        """
        db_name = 'db_' + random_str()
        table_name = 'table_' + random_str()
        try:
            client = create_mssql_cli_client()
            setup_query = u"CREATE DATABASE {0};"\
                u"USE {0};"\
                u"CREATE TABLE {1} (컬럼1 nvarchar(MAX), 컬럼2 int);"\
                u"INSERT INTO {1} VALUES (N'테스트1', 1);"\
                u"INSERT INTO {1} VALUES (N'테스트2', 2);"\
                .format(db_name, table_name)
            for rows, columns, status, statement, is_error in client.execute_query(setup_query):
                assert is_error == False

            select_query = u"SELECT * FROM {0};".format(table_name)
            for rows, columns, status, statement, is_error in client.execute_query(select_query):
                assert is_error == False
                assert columns[0] == '\xec\xbb\xac\xeb\x9f\xbc1'
                assert columns[1] == '\xec\xbb\xac\xeb\x9f\xbc2'
                assert rows[0][0] == '\xed\x85\x8c\xec\x8a\xa4\xed\x8a\xb81'
                assert rows[1][0] == '\xed\x85\x8c\xec\x8a\xa4\xed\x8a\xb82'
        finally:
            clean_up_query = u"USE master; DROP DATABASE {0};".format(db_name)
            for rows, columns, status, statement, is_error in client.execute_query(clean_up_query):
                assert is_error == False
            shutdown(client)


if __name__ == u'__main__':
    unittest.main()
