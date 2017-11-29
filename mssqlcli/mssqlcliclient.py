# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import logging
from time import sleep
import time
import uuid
import click
import sqlparse

from mssqlcli import mssqlqueries
from mssqlcli.jsonrpc.contracts import connectionservice, queryexecutestringservice as queryservice
from mssqlcli.sqltoolsclient import SqlToolsClient
from mssqlcli.packages.parseutils.meta import ForeignKey

logger = logging.getLogger(u'mssqlcli.mssqlcliclient')
time_wait_if_no_response = 0.05


def generate_owner_uri():
    return u'mssql-cli-' + uuid.uuid4().urn


class MssqlCliClient(object):

    def __init__(self, sql_tools_client, server_name, user_name, password,
                 authentication_type=u'SqlLogin', database=u'master', owner_uri=None, multiple_active_result_sets=True,
                 **kwargs):
        self.server_name = server_name
        self.user_name = user_name
        self.password = password
        self.authentication_type = authentication_type
        self.database = database
        self.owner_uri = owner_uri
        self.is_connected = False
        self.multiple_active_result_sets = multiple_active_result_sets
        self.extra_params = {k: v for k, v in kwargs.items()}
        self.sql_tools_client = sql_tools_client

        # If no owner_uri which depicts a connection is passed, generate one and use that.
        if not owner_uri:
            self.owner_uri = generate_owner_uri()

        logger.info(u'Initialized MssqlCliClient')

    def connect(self):
        """
        Connects to the SQL Server instance using specified credentials
        :return: OwnerUri if connection established else None
        """
        if self.is_connected:
            return self.owner_uri

        connection_params = {u'ServerName': self.server_name,
                              u'DatabaseName': self.database,
                              u'UserName': self.user_name,
                              u'Password': self.password,
                              u'AuthenticationType': self.authentication_type,
                              u'OwnerUri': self.owner_uri,
                              u'MultipleActiveResultSets': self.multiple_active_result_sets}

        connection_params.update(self.extra_params)

        connection_request = self.sql_tools_client.create_request(u'connection_request', connection_params)
        connection_request.execute()

        while not connection_request.completed():
            response = connection_request.get_response()
            if response:
                response = connectionservice.handle_connection_response(response)
            else:
                time.sleep(time_wait_if_no_response)

        if response and response.connection_id:
            # response owner_uri should be the same as owner_uri used, else something is weird :)
            assert response.owner_uri == self.owner_uri
            self.is_connected = True
            logger.info(u'Connection Successful. Connection Id {0}'.format(response.connection_id))
            return self.owner_uri
        else:
            logger.info(u'Connection did not succeed')
            return None

    def execute_multi_statement_single_batch(self, query):
        # Remove spaces, EOL and semi-colons from end
        query = query.strip()
        if not query:
            yield None, None, None, query, False
        else:
            for sql in sqlparse.split(query):
                # Remove spaces, EOL and semi-colons from end
                sql = sql.strip().rstrip(';')
                if not sql:
                    yield None, None, None, sql, False
                    continue
                yield self.execute_single_batch_query(sql)

    def execute_single_batch_query(self, query):
        if not self.is_connected:
            click.secho(u'No connection established with the server.', err=True, fg='red')
            exit(1)

        query_request = self.sql_tools_client.create_request(u'query_execute_string_request',
                                                             {u'OwnerUri': self.owner_uri, u'Query': query})
        query_request.execute()
        query_message=None
        while not query_request.completed():
            query_response = query_request.get_response()
            if query_response:
                if isinstance(query_response, queryservice.QueryMessageEvent):
                    query_message = query_response
            else:
                sleep(time_wait_if_no_response)

        if query_response.exception_message:
            logger.error(u'Query response had an exception')
            return self.tabular_results_generator(
                column_info=None,
                result_rows=None,
                query=query,
                message=query_response.exception_message,
                is_error=True)

        if (not query_response.batch_summaries[0].result_set_summaries) or \
            (query_response.batch_summaries[0].result_set_summaries[0].row_count == 0):
            return self.tabular_results_generator(
                column_info=None,
                result_rows=None,
                query=query,
                message=query_message.message if query_message else u'',
                is_error=query_message.is_error if query_message else query_response.batch_summaries[0].has_error)

        else:
            query_subset_request = self.sql_tools_client.create_request(u'query_subset_request',
                        {u'OwnerUri': query_response.owner_uri,
                          u'BatchIndex': query_response.batch_summaries[0].result_set_summaries[0].batch_id,
                          u'ResultSetIndex': query_response.batch_summaries[0].result_set_summaries[0].id,
                          u'RowsStartIndex': 0,
                          u'RowCount': query_response.batch_summaries[0].result_set_summaries[0].row_count})

            query_subset_request.execute()
            while not query_subset_request.completed():
                subset_response = query_subset_request.get_response()
                if not subset_response:
                    sleep(time_wait_if_no_response)

            if subset_response.error_message:
                logger.error(u'Error obtaining result sets for query response')
                return self.tabular_results_generator(
                    column_info=None,
                    result_rows=None,
                    query=query,
                    message=subset_response.error_message,
                    is_error=True)

            logger.info(u'Obtained result set for query')
            return self.tabular_results_generator(
                column_info=query_response.batch_summaries[0].result_set_summaries[0].column_info,
                result_rows=subset_response.rows,
                query=query,
                message=query_message.message if query_message else u'')

    def tabular_results_generator(self, column_info, result_rows, query, message, is_error=False):
        # Returns a generator of rows, columns, status(rows affected) or message, sql (the query), is_error
        if is_error:
            return None, None, message, query, is_error

        columns = [col.column_name for col in column_info] if column_info else None
        rows = ([[cell.display_value for cell in result_row.result_cells] for result_row in result_rows]) if result_rows else ()

        return rows, columns, message, query, is_error

    def schemas(self):
        """ Returns a list of schema names"""
        query = mssqlqueries.get_schemas()
        logger.info(u'Schemas query: {0}'.format(query))
        return [x[0] for x in self.execute_single_batch_query(query)[0]]

    def databases(self):
        """ Returns a list of database names"""
        query = mssqlqueries.get_databases()
        logger.info(u'Databases query: {0}'.format(query))
        return [x[0] for x in self.execute_single_batch_query(query)[0]]

    def tables(self):
        """ Yields (schema_name, table_name) tuples"""
        query = mssqlqueries.get_tables()
        logger.info(u'Tables query: {0}'.format(query))
        for row in self.execute_single_batch_query(query)[0]:
            yield (row[0], row[1])

    def table_columns(self):
        """ Yields (schema_name, table_name, column_name, data_type, column_default) tuples"""
        query = mssqlqueries.get_table_columns()
        logger.info(u'Table columns query: {0}'.format(query))
        for row in self.execute_single_batch_query(query)[0]:
            yield (row[0], row[1], row[2], row[3], row[4])

    def views(self):
        """ Yields (schema_name, table_name) tuples"""
        query = mssqlqueries.get_views()
        logger.info(u'Views query: {0}'.format(query))
        for row in self.execute_single_batch_query(query)[0]:
            yield (row[0], row[1])

    def view_columns(self):
        """ Yields (schema_name, table_name, column_name, data_type, column_default) tuples"""
        query = mssqlqueries.get_view_columns()
        logger.info(u'View columns query: {0}'.format(query))
        for row in self.execute_single_batch_query(query)[0]:
            yield (row[0], row[1], row[2], row[3], row[4])

    def user_defined_types(self):
        """ Yields (schema_name, type_name) tuples"""
        query = mssqlqueries.get_user_defined_types()
        logger.info(u'UDTs query: {0}'.format(query))
        for row in self.execute_single_batch_query(query)[0]:
            yield (row[0], row[1])

    def foreignkeys(self):
        """ Yields (parent_schema, parent_table, parent_column, child_schema, child_table, child_column) typles"""
        query = mssqlqueries.get_foreignkeys()
        logger.info(u'Foreign keys query: {0}'.format(query))
        for row in self.execute_single_batch_query(query)[0]:
            yield ForeignKey(*row)

    def shutdown(self):
        self.sql_tools_client.shutdown()
        logger.info(u'Shutdown MssqlCliClient')


def reset_connection_and_clients(sql_tools_client, *mssqlcliclients):
    """
    Restarts the sql_tools_client and establishes new connections for each of the
    mssqlcliclients passed
    """
    try:
        sql_tools_client.shutdown()
        new_tools_client = SqlToolsClient()
        for mssqlcliclient in mssqlcliclients:
            mssqlcliclient.sql_tools_client = new_tools_client
            mssqlcliclient.is_connected = False
            mssqlcliclient.owner_uri = generate_owner_uri()
            if not mssqlcliclient.connect():
                click.secho('Unable reconnect to server {0}; database {1}.'.format(mssqlcliclient.server_name, mssqlcliclient.database),
                            err=True, fg='red')
                logger.info(u'Unable to reset connection to server {0}; database {1}'.format(mssqlcliclient.server_name, mssqlcliclient.database))
                exit(1)

    except Exception as e:
        logger.error(u'Error in reset_connection : {0}'.format(e.message))
        raise e