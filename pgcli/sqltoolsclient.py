# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import logging
import subprocess
import io
import time
import sys

import pgcli.mssqltoolsservice as mssqltoolsservice
import pgcli.jsonrpc.jsonrpcclient as json_rpc_client
import pgcli.jsonrpc.contracts.connectionservice as connection
import pgcli.jsonrpc.contracts.queryexecutestringservice as query

logger = logging.getLogger(u'mssqlcli.sqltoolsclient')
sqltoolsservice_args = [mssqltoolsservice.get_executable_path()]


class SqlToolsClient(object):
    """
        Create sql tools service requests.
    """

    def __init__(self, input_stream=None, output_stream=None):
        """
            Initializes the sql tools client.
            Input and output streams for JsonRpcClient are taken as optional params,
            Else a SqlToolsService process is started and its stdin and stdout is used.
        """
        self.current_id = 1
        self.tools_service_process = None

        if input_stream and output_stream:
            self.json_rpc_client = json_rpc_client.JsonRpcClient(
                input_stream, output_stream)
        else:
            self.tools_service_process = subprocess.Popen(
                sqltoolsservice_args,
                bufsize=0,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE)

            self.json_rpc_client = json_rpc_client.JsonRpcClient(
                self.tools_service_process.stdin,
                io.open(
                    self.tools_service_process.stdout.fileno(),
                    u'rb',
                    buffering=0,
                    closefd=False))

            logger.info(u'SqlToolsService process id: {0}'.format(self.tools_service_process.pid))

        self.json_rpc_client.start()
        logger.info(u'Sql Tools Client Initialized')

    def create_request(self, request_type, parameters):
        """
            Create request of request type passed in.
        """
        request = None

        if request_type == u'connection_request':
            logger.info(u'SqlToolsClient connection request Id {0}'.format(self.current_id))
            request = connection.ConnectionRequest(self.current_id, self.json_rpc_client, parameters)
            self.current_id += 1
            return request

        if request_type == u'query_execute_string_request':
            logger.info(u'SqlToolsClient execute string request Id {0}'.format(self.current_id))
            request = query.QueryExecuteStringRequest(self.current_id, self.json_rpc_client, parameters)
            self.current_id += 1
            return request

        if request_type == u'query_subset_request':
            logger.info(u'SqlToolsClient subset request Id {0}'.format(self.current_id))
            request = query.QuerySubsetRequest(self.current_id, self.json_rpc_client, parameters)
            self.current_id += 1
            return request

    def shutdown(self):
        self.json_rpc_client.shutdown()

        if self.tools_service_process:
            logger.info(u'Shutting down Sql Tools Client Process Id: {0}'.format(self.tools_service_process.pid))
            self.tools_service_process.kill()
            # Give the tools service process time to die
            time.sleep(0.1)
            # Close the stdout file handle or else we would get a resource warning (found via pytest).
            # This must be closed after the process is killed, otherwise we would block because the process is using
            # it's stdout.
            self.tools_service_process.stdout.close()
            # None value indicates process has not terminated.
            if not self.tools_service_process.poll():
                sys.stderr.write(
                    u'\nSql Tools Service process was not shut down properly.')
