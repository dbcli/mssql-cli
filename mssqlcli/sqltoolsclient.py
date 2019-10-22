import logging
import subprocess
import io
import time
import sys
import uuid

import mssqlcli.mssqltoolsservice as mssqltoolsservice
import mssqlcli.jsonrpc.jsonrpcclient as json_rpc_client
import mssqlcli.jsonrpc.contracts.connectionservice as connection
import mssqlcli.jsonrpc.contracts.queryexecutestringservice as query
from .config import config_location

logger = logging.getLogger(u'mssqlcli.sqltoolsclient')


class SqlToolsClient(object):
    """
        Create sql tools service requests.
    """
    CONNECTION_REQUEST = u'connection_request'
    QUERY_EXECUTE_STRING_REQUEST = u'query_execute_string_request'
    QUERY_SUBSET_REQUEST = u'query_subset_request'

    def __init__(self, input_stream=None, output_stream=None, enable_logging=False):
        """
            Initializes the sql tools client.
            Input and output streams for JsonRpcClient are taken as optional params,
            Else a SqlToolsService process is started and its stdin and stdout is used.
        """
        self.current_id = uuid.uuid4().int
        self.tools_service_process = None

        sqltoolsservice_args = [mssqltoolsservice.get_executable_path()]

        if enable_logging:
            sqltoolsservice_args.append('--enable-logging')
            sqltoolsservice_args.append('--log-dir')
            sqltoolsservice_args.append(config_location())

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

    def create_request(self, request_type, parameters, owner_uri):
        """
            Create request of request type passed in.
        """
        request = None
        self.current_id = str(uuid.uuid4().int)

        if request_type == u'connection_request':
            logger.info(u'SqlToolsClient connection request Id {0} and owner Uri {1}'.format(self.current_id,
                                                                                             owner_uri))
            request = connection.ConnectionRequest(self.current_id, owner_uri, self.json_rpc_client, parameters)
            return request

        if request_type == u'query_execute_string_request':
            logger.info(u'SqlToolsClient execute string request Id {0} and owner Uri {1}'.format(self.current_id,
                                                                                                 owner_uri))
            request = query.QueryExecuteStringRequest(self.current_id, owner_uri, self.json_rpc_client, parameters)
            return request

        if request_type == u'query_subset_request':
            logger.info(u'SqlToolsClient subset request Id {0} and owner Uri {1}'.format(self.current_id,
                                                                                         owner_uri))
            request = query.QuerySubsetRequest(self.current_id, owner_uri, self.json_rpc_client, parameters)
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
