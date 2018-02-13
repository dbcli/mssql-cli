import logging
from mssqlcli.jsonrpc.contracts import Request

logger = logging.getLogger(u'mssqlcli.queryexecutestringservice')


class QueryExecuteStringRequest(Request):
    """
        Uses SQL Tools Service query/executeString method.
    """

    METHOD_NAME = u'query/executeString'

    def __init__(self, id, owner_uri, json_rpc_client, parameters):
        self.id = id
        self.owner_uri = owner_uri
        self.finished = False
        self.json_rpc_client = json_rpc_client
        self.params = QueryExecuteStringParams(parameters)

    def get_response(self):
        """
            Get latest response, event or exception if occured.
        """
        try:
            response = self.json_rpc_client.get_response(self.id, self.owner_uri)

            decoded_response = None
            if response:
                decoded_response = self.decode_response(response)

            if isinstance(decoded_response, QueryCompleteEvent) or \
               isinstance(decoded_response, QueryExecuteErrorResponseEvent):
                self.finished = True
                self.json_rpc_client.request_finished(self.id)
                self.json_rpc_client.request_finished(self.owner_uri)

            return decoded_response

        except Exception as error:
            self.finished = True
            self.json_rpc_client.request_finished(self.id)
            self.json_rpc_client.request_finished(self.owner_uri)
            return QueryCompleteEvent(
                {u'params': None}, exception_message=str(error)
            )

    def execute(self):
        self.json_rpc_client.submit_request(
            self.METHOD_NAME, self.params.format(), self.id)

    def completed(self):
        """
            Get current request state.
        """
        return self.finished

    def decode_response(self, response):
        if u'method' in response and response[u'method'] == u'query/complete':
            return QueryCompleteEvent(response)
        elif u'method' in response and response[u'method'] == u'query/message':
            return QueryMessageEvent(response)
        elif u'error' in response:
            return QueryExecuteErrorResponseEvent(response)

        return response


class QueryExecuteStringParams(object):
    def __init__(self, parameters):
        self.owner_uri = parameters['OwnerUri']
        self.query = parameters['Query']

    def format(self):
        return {u'OwnerUri': self.owner_uri,
                u'Query': self.query}


class QueryExecuteErrorResponseEvent(object):
    def __init__(self, parameters):
        inner_params = parameters[u'error']
        self.exception_message = inner_params[u'message'] if u'message' in inner_params else ''
        self.error_code = inner_params[u'code'] if u'code' in inner_params else ''


class QueryMessageEvent(object):
    def __init__(self, parameters):
        inner_params = parameters[u'params']
        self.owner_uri = inner_params[u'ownerUri']
        self.is_error = inner_params[u'message'][u'isError']
        self.batch_id = inner_params[u'message'][u'batchId']
        self.message = inner_params[u'message'][u'message']


class QueryCompleteEvent(object):
    def __init__(self, parameters, exception_message=None):
        inner_params = parameters[u'params']
        if inner_params:
            self.owner_uri = inner_params[u'ownerUri']
            self.batch_summaries = []
            for batch_summary in inner_params[u'batchSummaries']:
                self.batch_summaries.append(BatchSummary(batch_summary))

        self.exception_message = exception_message


class BatchSummary(object):
    def __init__(self, parameters):
        self.has_error = parameters[u'hasError']
        self.id = parameters[u'id']
        self.execution_time_elapsed = parameters[u'executionElapsed']
        self.result_set_summaries = []
        for result_set_summary in parameters[u'resultSetSummaries']:
            self.result_set_summaries.append(
                ResultSetSummary(result_set_summary))


class ResultSetSummary(object):
    def __init__(self, parameters):
        self.batch_id = parameters[u'batchId']
        self.id = parameters[u'id']
        self.row_count = parameters[u'rowCount']
        self.column_info = []
        for column in parameters[u'columnInfo']:
            self.column_info.append(Column(column))


class Column(object):
    def __init__(self, parameters):
        self.column_name = parameters[u'columnName']
        self.data_type_name = parameters[u'dataTypeName']


class QuerySubsetRequest(Request):
    """
        SqlToolsService QuerySubset Request.
    """

    METHOD_NAME = u'query/subset'

    def __init__(self, id, owner_uri, json_rpc_client, parameters):
        self.id = id
        self.owner_uri = owner_uri
        self.finished = False
        self.json_rpc_client = json_rpc_client
        self.params = QuerySubsetParams(parameters)

    def completed(self):
        """
            Get current request state.
        """
        return self.finished

    def get_response(self):
        try:
            response = self.json_rpc_client.get_response(self.id, self.owner_uri)
            decoded_response = None
            if response:
                decoded_response = self.decode_response(response)

            if isinstance(decoded_response, ResultSubset):
                self.finished = True
                self.json_rpc_client.request_finished(self.id)
                self.json_rpc_client.request_finished(self.owner_uri)

            return decoded_response

        except Exception as error:
            self.finished = True
            self.json_rpc_client.request_finished(self.id)
            self.json_rpc_client.request_finished(self.owner_uri)
            return ResultSubset(None, error_message=str(error))

    def execute(self):
        self.json_rpc_client.submit_request(
            self.METHOD_NAME, self.params.format(), self.id)

    def decode_response(self, response):
        if u'result' in response:
            return ResultSubset(response)
        elif u'error' in response:
            return ResultSubset(
                None, error_message=response[u'error']['message'])


class QuerySubsetParams(object):
    def __init__(self, parameters):
        self.owner_uri = parameters[u'OwnerUri']
        self.batch_index = parameters[u'BatchIndex']
        self.result_set_index = parameters[u'ResultSetIndex']
        self.rows_start_index = parameters[u'RowsStartIndex']
        self.row_count = parameters[u'RowCount']

    def format(self):
        return {u'OwnerUri': self.owner_uri,
                u'BatchIndex': self.batch_index,
                u'ResultSetIndex': self.result_set_index,
                u'RowsStartIndex': self.rows_start_index,
                u'RowsCount': self.row_count}


class ResultSubset(object):
    def __init__(self, parameters, error_message=None):
        if not error_message:
            inner_params = parameters[u'result'][u'resultSubset']
            self.row_count = inner_params[u'rowCount']
            self.rows = []
            for row in inner_params[u'rows']:
                self.rows.append(ResultRow(row))

        self.error_message = error_message


class ResultRow(object):
    def __init__(self, parameter):
        self.result_cells = []
        for result_cell in parameter:
            self.result_cells.append(ResultCell(result_cell))


class ResultCell(object):
    def __init__(self, parameter):
        self.display_value = parameter[u'displayValue']
        self.row_id = parameter[u'rowId']
        self.is_null = parameter[u'isNull']
