# coding=utf-8
import os
import io
from time import sleep
import pytest
import mssqlcli.sqltoolsclient as sqltoolsclient
from mssqlcli.jsonrpc.jsonrpcclient import JsonRpcWriter
from mssqltestutils import (
    create_mssql_cli,
    create_mssql_cli_options,
    create_mssql_cli_client,
    create_test_db,
    clean_up_test_db,
    shutdown,
    random_str
)


# Please Note: These tests cannot be run offline.

class MssqlCliClient:   # pylint: disable=too-few-public-methods
    """ Creates client fixture to be used for tests. """

    @staticmethod
    @pytest.fixture(scope='function')
    def client():
        cl = create_mssql_cli_client()
        yield cl
        shutdown(cl)

    @staticmethod
    @pytest.fixture(scope='class')
    def client_with_db():
        db_name = create_test_db()

        # create options with db name
        options = create_mssql_cli_options()
        options.database = db_name

        cl = create_mssql_cli_client(options)
        yield cl

        # cleanup
        shutdown(cl)
        clean_up_test_db(db_name)

class TestMssqlCliClientConnection(MssqlCliClient):
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
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jsonrpc',
                             'baselines', file_name))

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

    @staticmethod
    def test_connection():
        """
            Verify a successful connection via returned owner uri.
        """
        try:
            client = create_mssql_cli_client(owner_uri=u'connectionservicetest')

            assert client.owner_uri == u'connectionservicetest'
        finally:
            shutdown(client)

    @staticmethod
    def test_json_writer_extra_params(client):
        """
            Verify JSON RPC accepts extra paramaters.
        """
        try:
            extra_params = client.extra_params
            json_writer = JsonRpcWriter(io.BytesIO())
            json_writer.send_request(u'test/method', extra_params, request_id=1)
        finally:
            json_writer.close()

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


class TestMssqlCliClientQuery(MssqlCliClient):
    """ Unit tests for executing queries with mssql-cli client. """

    @staticmethod
    def test_get_query_results(client):
        """
            Verify number of rows returned and returned query.
        """
        test_query = u"""select 1 as [ShiftID], 'Day' as [Name] UNION ALL\
                            select 2, N'魚' UNION ALL\
                            select 3, 'Night'"""

        for rows, _, _, query, _ in client.execute_query(test_query):
            assert len(rows) == 3
            assert query == test_query

    @pytest.mark.unstable
    def test_schema_table_views_and_columns_query(self, client_with_db):
        """
            Verify mssqlcliclient's tables, views, columns, and schema are populated.
            Note: This test should run against a database that the credentials
                  MSSQL_CLI_USER and MSSQL_CLI_PASSWORD have write access to.
        """
        client = client_with_db

        # create random strings for entities
        tabletest1 = "test_%s" % random_str()
        tabletest2 = "test_%s" % random_str()
        viewtest = "test_%s" % random_str()
        schematest = "test_%s" % random_str()

        queries_create = [
            'CREATE TABLE %s (a int, b varchar(25));' % tabletest1,
            'CREATE TABLE %s (x int, y varchar(25), z bit);' % tabletest2,
            'CREATE VIEW %s as SELECT a from %s;' % (viewtest, tabletest1),
            'CREATE SCHEMA %s;' % schematest,
            'CREATE TABLE %s (a int);' % '.'.join([schematest, tabletest1])
        ]

        queries_drop = [
            'DROP TABLE IF EXISTS %s;' % tabletest1,
            'DROP TABLE IF EXISTS %s;' % tabletest2,
            'DROP VIEW IF EXISTS %s;' % viewtest,
            'DROP TABLE IF EXISTS %s;' % ".".join([schematest, tabletest1]),
            'DROP SCHEMA IF EXISTS %s;' % schematest
        ]

        try:
            # drop entities in beginning (in case tables exist)
            self.execute_queries(client, queries_drop)
            self.execute_queries(client, queries_create)

            assert (schematest, tabletest1) in set(client.get_tables())
            assert ('dbo', viewtest) in set(client.get_views())
            assert (schematest, tabletest1, 'a', 'int', 'NULL') in set(client.get_table_columns())
            assert ('dbo', viewtest, 'a', 'int', 'NULL') in set(client.get_view_columns())
            assert schematest in client.get_schemas()
        except Exception as e:
            raise AssertionError(e)
        finally:
            self.execute_queries(client, queries_drop)

    @pytest.mark.unstable
    def test_stored_proc_multiple_result_sets(self, client_with_db):
        """
            Verify the results of running a stored proc with multiple result sets
        """
        client = client_with_db

        create_stored_proc = u"CREATE PROC sp_mssqlcli_multiple_results " \
                        u"AS " \
                        u"BEGIN " \
                        u"SELECT 'Morning' as [Name] UNION ALL select 'Evening' " \
                        u"SELECT 'Dawn' as [Name] UNION ALL select 'Dusk' " \
                        u"UNION ALL select 'Midnight' " \
                        u"END"
        exec_stored_proc = u"EXEC sp_mssqlcli_multiple_results"
        del_stored_proc = u"DROP PROCEDURE sp_mssqlcli_multiple_results"

        try:
            self.execute_queries(client, [create_stored_proc])
            row_counts = []
            for rows, _, _, _, _ in client.execute_query(exec_stored_proc):
                row_counts.append(len(rows))
            assert row_counts[0] == 2
            assert row_counts[1] == 3
        except Exception as e:
            raise AssertionError(e)
        finally:
            self.execute_queries(client, [del_stored_proc])

    @staticmethod
    def execute_queries(client, queries):
        """ Executes a batch of queries. """
        for query in queries:
            for _, _, status, _, is_error in client.execute_query(query):
                if is_error:
                    raise AssertionError("Query execution failed: {}".format(status))
        return True


class TestMssqlCliClientMultipleStatement(MssqlCliClient):
    test_data = [
        # random strings used to test for errors with non-existing tables
        (u"select 'Morning' as [Name] UNION ALL select 'Evening'; " +
         u"select 1;", [2, 1]),
        (u"select 1; select 'foo' from %s;" % random_str(), [1, 0]),
        (u"select 'foo' from %s; select 2;" % random_str(), [0, 1])
    ]

    @staticmethod
    @pytest.mark.parametrize("query_str, rows_outputted", test_data)
    def test_mssqlcliclient_multiple_statement(client, query_str, rows_outputted):
        """
            Verify correct execution of queries separated by semi-colon
        """

        for (i, (rows, _, _, query_executed, is_error)) in \
            enumerate(client.execute_query(query_str)):

            queries = ["{};".format(query) for query in query_str.split(';')]
            assert query_executed == queries[i].strip()
            assert len(rows) == rows_outputted[i]
            assert (is_error and len(rows) == 0) or (not is_error)
