
import copy
import logging
import time
import uuid
from time import sleep

import click
import sqlparse

from mssqlcli import mssqlqueries
from mssqlcli.jsonrpc.contracts import connectionservice, queryexecutestringservice as queryservice
from mssqlcli.packages import special
from mssqlcli.packages.parseutils.meta import ForeignKey

logger = logging.getLogger(u'mssqlcli.mssqlcliclient')
time_wait_if_no_response = 0.05


def generate_owner_uri():
    return u'mssql-cli-' + uuid.uuid4().urn


class MssqlCliClient(object):

    def __init__(self, mssqlcli_options, sql_tools_client, owner_uri=None, **kwargs):

        self.server_name = mssqlcli_options.server
        if ',' in mssqlcli_options.server:
            self.prompt_host, self.prompt_port = self.server_name.split(',')
        else:
            self.prompt_host = mssqlcli_options.server
            self.prompt_port = 1433

        self.user_name = mssqlcli_options.username
        self.password = mssqlcli_options.password
        self.authentication_type = u'Integrated' if mssqlcli_options.integrated_auth else u'SqlLogin'
        self.database = mssqlcli_options.database
        self.encrypt = mssqlcli_options.encrypt
        self.trust_server_certificate = mssqlcli_options.trust_server_certificate
        self.connection_timeout = mssqlcli_options.connection_timeout
        self.application_intent = mssqlcli_options.application_intent
        self.multi_subnet_failover = mssqlcli_options.multi_subnet_failover
        self.packet_size = mssqlcli_options.packet_size

        self.extra_params = {k: v for k, v in kwargs.items()}
        self.owner_uri = owner_uri
        self.is_connected = False
        self.sql_tools_client = sql_tools_client
        self.server_version = None
        self.server_edition = None
        self.is_cloud = False

        if not owner_uri:
            self.owner_uri = generate_owner_uri()

        logger.info(u'Initialized MssqlCliClient with owner Uri {}'.format(self.owner_uri))

    def get_base_connection_params(self):
        return {u'ServerName': self.server_name,
                u'DatabaseName': self.database,
                u'UserName': self.user_name,
                u'Password': self.password,
                u'AuthenticationType': self.authentication_type,
                u'OwnerUri': self.owner_uri
                }

    def add_optional_connection_params(self, base_connection_params):
        if self.encrypt:
            base_connection_params[u'Encrypt'] = self.encrypt
        if self.trust_server_certificate:
            base_connection_params[u'TrustServerCertificate'] = self.trust_server_certificate
        if self.connection_timeout:
            base_connection_params[u'ConnectTimeout'] = self.connection_timeout
        if self.application_intent:
            base_connection_params[u'ApplicationIntent'] = self.application_intent
        if self.multi_subnet_failover:
            base_connection_params[u'MultiSubnetFailover'] = self.multi_subnet_failover
        if self.packet_size:
            base_connection_params[u'PacketSize'] = self.packet_size

        base_connection_params.update(self.extra_params)

        return base_connection_params

    def connect_to_database(self):
        connection_params = self.get_base_connection_params()
        connection_params = self.add_optional_connection_params(connection_params)

        owner_uri, error_messages = self.execute_connection_request_with(connection_params)

        return owner_uri, error_messages

    def execute_connection_request_with(self, connection_params):
        if self.is_connected:
            return self.owner_uri, []

        connection_request = self.sql_tools_client.create_request(u'connection_request',
                                                                  connection_params,
                                                                  self.owner_uri)
        connection_request.execute()
        error_messages = []
        response = None

        while not connection_request.completed():
            response = connection_request.get_response()

            if isinstance(response, connectionservice.ConnectionCompleteEvent):
                if response.error_message:
                    error_messages.append(u'Error message: {}'.format(response.error_message))
                if response.messages:
                    logger.error(response.messages)
            else:
                time.sleep(time_wait_if_no_response)

        if response and response.connection_id:
            assert response.owner_uri == self.owner_uri
            self.is_connected = True
            self.server_version = response.server_version
            self.server_edition = response.server_edition
            self.is_cloud = response.is_cloud

            logger.info(
                u'Connection Successful. Connection Id {0}'.format(
                    response.connection_id))

            return self.owner_uri, []

        return None, error_messages

    def execute_multi_statement_single_batch(self, query):
        # Try to run first as special command
        try:
            for rows, columns, status, statement, is_error in special.execute(self, query):
                yield rows, columns, status, statement, is_error
        except special.CommandNotFound:
            # Execute as normal sql
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
                    for rows, columns, status, statement, is_error in self.execute_single_batch_query(sql):
                        yield rows, columns, status, statement, is_error

    def execute_single_batch_query(self, query):
        if not self.is_connected:
            click.secho(
                u'No connection established with the server.',
                err=True,
                fg='yellow')
            exit(1)

        query_request = self.sql_tools_client.create_request(u'query_execute_string_request',
                                                             {u'OwnerUri': self.owner_uri,
                                                              u'Query': query},
                                                             self.owner_uri)
        query_request.execute()
        query_messages = []
        while not query_request.completed():
            query_response = query_request.get_response()
            if isinstance(query_response, queryservice.QueryMessageEvent):
                query_messages.append(query_response)
            else:
                sleep(time_wait_if_no_response)

        if query_response.exception_message:
            logger.error(u'Query response had an exception')
            yield self.tabular_results_generator(
                column_info=None,
                result_rows=None,
                query=query,
                message=query_response.exception_message,
                is_error=True)
            return

        if (not query_response.batch_summaries[0].result_set_summaries) or \
           (query_response.batch_summaries[0].result_set_summaries[0].row_count == 0):
            yield self.tabular_results_generator(
                column_info=None,
                result_rows=None,
                query=query,
                message=query_messages[0].message if query_messages else u'',
                is_error=query_messages[0].is_error if query_messages else query_response.batch_summaries[0].has_error)

        else:
            for result_set_summary in query_response.batch_summaries[0].result_set_summaries:
                query_subset_request = self.sql_tools_client.create_request(u'query_subset_request',
                                                                            {u'OwnerUri': query_response.owner_uri,
                                                                             u'BatchIndex': result_set_summary.batch_id,
                                                                             u'ResultSetIndex': result_set_summary.id,
                                                                             u'RowsStartIndex': 0,
                                                                             u'RowCount': result_set_summary.row_count},
                                                                            self.owner_uri)

                query_subset_request.execute()
                while not query_subset_request.completed():
                    subset_response = query_subset_request.get_response()
                    if not subset_response:
                        sleep(time_wait_if_no_response)

                logger.info('Getting response for id {}'.format(query_subset_request.id))
                if subset_response.error_message:
                    logger.error(u'Error obtaining result sets for query response for id {}'.format(query_subset_request.id))
                    logger.error(u'Error Message: {}'.format(subset_response.error_message))
                    yield self.tabular_results_generator(
                        column_info=None,
                        result_rows=None,
                        query=query,
                        message=subset_response.error_message,
                        is_error=True)

                yield self.tabular_results_generator(
                    column_info=result_set_summary.column_info,
                    result_rows=subset_response.rows,
                    query=query,
                    message=query_messages[result_set_summary.id].message if query_messages else u'')

    def tabular_results_generator(self, column_info, result_rows, query, message, is_error=False):
        # Returns a generator of rows, columns, status(rows affected) or
        # message, sql (the query), is_error
        if is_error:
            return (), None, message, query, is_error

        columns = [
            col.column_name for col in column_info] if column_info else None
        rows = ([[cell.display_value for cell in result_row.result_cells]
                 for result_row in result_rows]) if result_rows else ()

        return rows, columns, message, query, is_error

    def clone(self):
        cloned_mssqlcli_client = copy.copy(self)
        cloned_mssqlcli_client.owner_uri = generate_owner_uri()
        cloned_mssqlcli_client.is_connected = False

        return cloned_mssqlcli_client

    def schemas(self):
        """ Returns a list of schema names"""
        query = mssqlqueries.get_schemas()
        logger.info(u'Schemas query: {0}'.format(query))
        for tabular_result in self.execute_single_batch_query(query):
            return [x[0] for x in tabular_result[0]]

    def databases(self):
        """ Returns a list of database names"""
        query = mssqlqueries.get_databases()
        logger.info(u'Databases query: {0}'.format(query))
        for tabular_result in self.execute_single_batch_query(query):
            return [x[0] for x in tabular_result[0]]

    def tables(self):
        """ Yields (schema_name, table_name) tuples"""
        query = mssqlqueries.get_tables()
        logger.info(u'Tables query: {0}'.format(query))
        for tabular_result in self.execute_single_batch_query(query):
            for row in tabular_result[0]:
                yield (row[0], row[1])

    def table_columns(self):
        """ Yields (schema_name, table_name, column_name, data_type, column_default) tuples"""
        query = mssqlqueries.get_table_columns()
        logger.info(u'Table columns query: {0}'.format(query))
        for tabular_result in self.execute_single_batch_query(query):
            for row in tabular_result[0]:
                yield (row[0], row[1], row[2], row[3], row[4])

    def views(self):
        """ Yields (schema_name, table_name) tuples"""
        query = mssqlqueries.get_views()
        logger.info(u'Views query: {0}'.format(query))
        for tabular_result in self.execute_single_batch_query(query):
            for row in tabular_result[0]:
                yield (row[0], row[1])

    def view_columns(self):
        """ Yields (schema_name, table_name, column_name, data_type, column_default) tuples"""
        query = mssqlqueries.get_view_columns()
        logger.info(u'View columns query: {0}'.format(query))
        for tabular_result in self.execute_single_batch_query(query):
            for row in tabular_result[0]:
                yield (row[0], row[1], row[2], row[3], row[4])

    def user_defined_types(self):
        """ Yields (schema_name, type_name) tuples"""
        query = mssqlqueries.get_user_defined_types()
        logger.info(u'UDTs query: {0}'.format(query))
        for tabular_result in self.execute_single_batch_query(query):
            for row in tabular_result[0]:
                yield (row[0], row[1])

    def foreignkeys(self):
        """ Yields (parent_schema, parent_table, parent_column, child_schema, child_table, child_column) typles"""
        query = mssqlqueries.get_foreignkeys()
        logger.info(u'Foreign keys query: {0}'.format(query))
        for tabular_result in self.execute_single_batch_query(query):
            for row in tabular_result[0]:
                yield ForeignKey(*row)

    def shutdown(self):
        self.sql_tools_client.shutdown()
        logger.info(u'Shutdown MssqlCliClient')
