# coding=utf-8
import os
import io
import unittest
from time import sleep
import mssqlcli.sqltoolsclient as sqltoolsclient
from mssqlcli.jsonrpc.jsonrpcclient import JsonRpcWriter
from mssqltestutils import (
    create_mssql_cli,
    create_mssql_cli_options,
    create_mssql_cli_client,
    shutdown,
    random_str
)


# All tests apart from test_mssqlcliclient_request_response require a live connection to an
# AdventureWorks2014 database with a hardcoded test server.
# Make modifications to mssqlutils.create_mssql_cli_client() to use a different server and database.
# Please Note: These tests cannot be run offline.
class MssqlCliClientTests(unittest.TestCase):
    """
        Tests for mssqlcliclient.py and sqltoolsclient.py.
    """
    @staticmethod
    def test_mssqlcliclient_request_response():
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

        try:
            with open(get_test_baseline(u'test_simple_query.txt'), u'r+b', buffering=0) \
                    as response_file:
                request_stream = io.BytesIO()
                sql_tools_client = sqltoolsclient.SqlToolsClient(
                    input_stream=request_stream, output_stream=response_file)

                # The sleep is required because py.test and logging have an issue with closing
                # the FileHandle in a non-thread safe way
                # issue24262
                sleep(0.5)

                mssql_cli_options = create_mssql_cli_options(integrated_auth=True)
                mssql_cli_client = create_mssql_cli_client(mssql_cli_options,
                                                           owner_uri=u'connectionservicetest',
                                                           sql_tools_client=sql_tools_client,
                                                           extra_bool_param=True,
                                                           extra_string_param=u'stringparam',
                                                           extra_int_param=5)
        finally:
            mssql_cli_client.shutdown()

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

            for rows, _, _, query, _ in client.execute_query(test_query):
                self.assertTrue(len(rows), 3)
                self.assertTrue(query, test_query)
        finally:
            shutdown(client)

    @staticmethod
    def test_json_writer_extra_params():
        """
            Verify JSON RPC accepts extra paramaters.
        """
        try:
            client = create_mssql_cli_client()
            extra_params = client.extra_params
            json_writer = JsonRpcWriter(io.BytesIO())
            json_writer.send_request(u'test/method', extra_params, id=1)
        finally:
            json_writer.close()
            shutdown(client)

    @staticmethod
    def test_schema_table_views_and_columns_query():
        """
            Verify mssqlcliclient's tables, views, columns, and schema are populated.
            Note: This test should run against a database that the credentials
                  MSSQL_CLI_USER and MSSQL_CLI_PASSWORD have write access to.
        """
        # create random strings for entities
        tabletest1 = "test_%s" % random_str()
        tabletest2 = "test_%s" % random_str()
        viewtest = "test_%s" % random_str()
        schematest = "test_%s" % random_str()

        def drop_entities(mssqlcli_client):
            list(mssqlcli_client.execute_query('DROP TABLE %s;' % tabletest1))
            list(mssqlcli_client.execute_query('DROP TABLE %s;' % tabletest2))
            list(mssqlcli_client.execute_query('DROP VIEW %s IF EXISTS;' % viewtest))
            list(mssqlcli_client.execute_query('DROP TABLE %s;' % "."
                                               .join([schematest, tabletest1])))
            list(mssqlcli_client.execute_query('DROP SCHEMA %s;' % schematest))

        try:
            client = create_mssql_cli_client()

            drop_entities(client)   # drop entities in beginning (in case tables exist)

            list(client.execute_query('CREATE TABLE %s (a int, b varchar(25));' % tabletest1))
            list(client.execute_query('CREATE TABLE %s (x int, y varchar(25), z bit);'
                                      % tabletest2))
            list(client.execute_query('CREATE VIEW %s as SELECT a from %s;'
                                      % (viewtest, tabletest1)))
            list(client.execute_query('CREATE SCHEMA %s;' % schematest))
            list(client.execute_query('CREATE TABLE %s (a int);'
                                      % '.'.join([schematest, tabletest1])))

            assert (schematest, tabletest1) in set(client.get_tables())
            assert ('dbo', viewtest) in set(client.get_views())
            assert (schematest, tabletest1, 'a', 'int', 'NULL') in set(client.get_table_columns())
            assert ('dbo', viewtest, 'a', 'int', 'NULL') in set(client.get_view_columns())
            assert schematest in client.get_schemas()

        finally:
            drop_entities(client)
            shutdown(client)

    @staticmethod
    def test_mssqlcliclient_reset_connection():
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
            multi_statement_query = (u"select 'Morning' as [Name] UNION ALL select 'Evening'; " +
                                     u"select 1;")
            multi_statement_query2 = u"select 1; select 'foo' from teapot;"
            multi_statement_query3 = u"select 'foo' from teapot; select 2;"
            for rows, _, _, query, is_error in client.execute_query(multi_statement_query):
                if query == u"select 'Morning' as [Name] UNION ALL select 'Evening'":
                    self.assertTrue(len(rows), 2)
                else:
                    self.assertTrue(len(rows), 1)

            for rows, _, _, query, is_error in \
                    client.execute_query(multi_statement_query2):
                if query == u"select 1":
                    self.assertTrue(len(rows) == 1)
                else:
                    self.assertTrue(is_error)

            for rows, _, _, query, is_error in \
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
                          u"SELECT 'Dawn' as [Name] UNION ALL select 'Dusk' " \
                          u"UNION ALL select 'Midnight' " \
                          u"END"
            exec_stored_proc = u"EXEC sp_mssqlcli_multiple_results"
            del_stored_proc = u"DROP PROCEDURE sp_mssqlcli_multiple_results"

            list(client.execute_query(create_stored_proc))
            row_counts = []
            for rows, _, _, _, _ in client.execute_query(exec_stored_proc):
                row_counts.append(len(rows))
            self.assertTrue(row_counts[0] == 2)
            self.assertTrue(row_counts[1] == 3)
            list(client.execute_query(del_stored_proc))
        finally:
            shutdown(client)


if __name__ == u'__main__':
    unittest.main()
