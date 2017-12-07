# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import io
import unittest
from time import sleep

import mssqlcli.sqltoolsclient as sqltoolsclient
import mssqlcli.mssqlcliclient as mssqlcliclient
from mssqlcli.jsonrpc.jsonrpcclient import JsonRpcWriter
from mssqlutils import create_mssql_cli_client, shutdown


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

        with open(get_test_baseline(u'select_from_humanresources_department_adventureworks2014.txt'), u'r+b', buffering=0) as response_file:
            request_stream = io.BytesIO()
            self.sql_tools_client = sqltoolsclient.SqlToolsClient(
                input_stream=request_stream, output_stream=response_file)

            # The sleep is required because py.test and logging have an issue with closing the FileHandle
            # in a non-thread safe way
            # issue24262
            sleep(0.5)

        self.client = mssqlcliclient.MssqlCliClient(self.sql_tools_client,
                                                    u'bro-hb',
                                                    u'*',
                                                    u'*',
                                                    authentication_type=u'Integrated',
                                                    database=u'AdventureWorks2014',
                                                    owner_uri=u'connectionservicetest',
                                                    extra_bool_param=True,
                                                    extra_string_param=u'stringparam',
                                                    extra_int_param=5)
        self.client.sql_tools_client.shutdown()

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

            rows, col, message, query, is_error = client.execute_single_batch_query(test_query)

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
            client.execute_single_batch_query('CREATE TABLE tabletest1 (a int, b varchar(25));')
            client.execute_single_batch_query('CREATE TABLE tabletest2 (x int, y varchar(25), z bit);')
            client.execute_single_batch_query('CREATE VIEW viewtest as SELECT a from tabletest1;')
            client.execute_single_batch_query('CREATE SCHEMA schematest;')
            client.execute_single_batch_query('CREATE TABLE schematest.tabletest1 (a int);')

            assert ('schematest', 'tabletest1') in set(client.tables())
            assert ('dbo', 'viewtest') in set(client.views())
            assert ('schematest', 'tabletest1', 'a', 'int', 'NULL') in set(client.table_columns())
            assert ('dbo', 'viewtest', 'a', 'int', 'NULL') in set(client.view_columns())
            assert 'schematest' in client.schemas()

        finally:
            client.execute_single_batch_query('DROP TABLE tabletest1;')
            client.execute_single_batch_query('DROP TABLE tabletest2;')
            client.execute_single_batch_query('DROP VIEW viewtest IF EXISTS;')
            client.execute_single_batch_query('DROP TABLE schematest.tabletest1;')
            client.execute_single_batch_query('DROP SCHEMA schematest;')
            shutdown(client)

    def test_mssqlcliclient_reset_connection(self):
        """
            Verify if the MssqlCliClient can successfully reset its connection
        """
        try:
            client = create_mssql_cli_client()
            mssqlcliclient.reset_connection_and_clients(client.sql_tools_client, client)
        finally:
            shutdown(client)

    def test_mssqlcliclient_multiple_statement(self):
        """
            Verify correct execution of queries separated by semi-colon
        """
        try:
            client = create_mssql_cli_client()
            multi_statement_query = u"select 'Morning' as [Name] UNION ALL select 'Evening'; select 1;"
            for rows, col, message, query, is_error in \
                client.execute_multi_statement_single_batch(multi_statement_query):
                if query == u"select 'Morning' as [Name] UNION ALL select 'Evening'":
                    self.assertTrue(len(rows), 2)
                else:
                    self.assertTrue(len(rows), 1)
        finally:
            shutdown(client)

if __name__ == u'__main__':
    unittest.main()
