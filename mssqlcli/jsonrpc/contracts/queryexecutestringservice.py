# pylint: disable=too-many-instance-attributes
# pylint: disable=too-few-public-methods

import logging
from mssqlcli.jsonrpc.contracts import Request

logger = logging.getLogger(u'mssqlcli.queryexecutestringservice')


class QueryExecuteStringRequest(Request):
    """
        Uses SQL Tools Service query/executeString method.
    """

    def __init__(self, request_id, owner_uri, json_rpc_client, parameters):
        super(QueryExecuteStringRequest, self).__init__(request_id, owner_uri, json_rpc_client,
                                                        QueryExecuteStringParams(parameters),
                                                        u'query/executeString',
                                                        (QueryCompleteEvent,
                                                         QueryExecuteErrorResponseEvent))

    @classmethod
    def response_error(cls, error):
        return QueryCompleteEvent(
            {u'params': None}, exception_message=str(error)
        )

    @staticmethod
    def decode_response(response):
        if u'method' in response and response[u'method'] == u'query/complete':
            return QueryCompleteEvent(response)
        if u'method' in response and response[u'method'] == u'query/message':
            return QueryMessageEvent(response)
        if u'error' in response:
            return QueryExecuteErrorResponseEvent(response)

        return response


class QueryExecuteStringParams:
    def __init__(self, parameters):
        self.owner_uri = parameters['OwnerUri']
        self.query = parameters['Query']

    def format(self):
        return {u'OwnerUri': self.owner_uri,
                u'Query': self.query}


class QueryExecuteErrorResponseEvent:
    def __init__(self, parameters):
        inner_params = parameters[u'error']
        self.exception_message = inner_params[u'message'] if u'message' in inner_params else ''
        self.error_code = inner_params[u'code'] if u'code' in inner_params else ''


class QueryMessageEvent:
    def __init__(self, parameters):
        inner_params = parameters[u'params']
        self.owner_uri = inner_params[u'ownerUri']
        self.is_error = inner_params[u'message'][u'isError']
        self.batch_id = inner_params[u'message'][u'batchId']
        self.message = inner_params[u'message'][u'message']


class QueryCompleteEvent:
    def __init__(self, parameters, exception_message=None):
        inner_params = parameters[u'params']
        if inner_params:
            self.owner_uri = inner_params[u'ownerUri']
            self.batch_summaries = []
            for batch_summary in inner_params[u'batchSummaries']:
                self.batch_summaries.append(BatchSummary(batch_summary))

        self.exception_message = exception_message


class BatchSummary:
    def __init__(self, parameters):
        self.has_error = parameters[u'hasError']
        self.request_id = parameters[u'id']
        self.execution_time_elapsed = parameters[u'executionElapsed']
        self.result_set_summaries = []
        for result_set_summary in parameters[u'resultSetSummaries']:
            self.result_set_summaries.append(
                ResultSetSummary(result_set_summary))


class ResultSetSummary:
    def __init__(self, parameters):
        self.batch_id = parameters[u'batchId']
        self.request_id = parameters[u'id']
        self.row_count = parameters[u'rowCount']
        self.column_info = []
        for column in parameters[u'columnInfo']:
            self.column_info.append(Column(column))


class Column:
    def __init__(self, parameters):
        self.column_name = parameters[u'columnName']
        self.data_type_name = parameters[u'dataTypeName']


class QuerySubsetRequest(Request):
    """
        SqlToolsService QuerySubset Request.
    """

    def __init__(self, request_id, owner_uri, json_rpc_client, parameters):
        super(QuerySubsetRequest, self).__init__(request_id, owner_uri, json_rpc_client,
                                                 QuerySubsetParams(parameters),
                                                 u'query/subset', ResultSubset)

    @classmethod
    def response_error(cls, error):
        return ResultSubset(None, error_message=str(error))

    @staticmethod
    def decode_response(response):
        result_subset = None

        if u'result' in response:
            result_subset = ResultSubset(response)
        elif u'error' in response:
            result_subset = ResultSubset(
                None, error_message=response[u'error']['message'])

        return result_subset


class QuerySubsetParams:
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


class ResultSubset:
    def __init__(self, parameters, error_message=None):
        if not error_message:
            inner_params = parameters[u'result'][u'resultSubset']
            self.row_count = inner_params[u'rowCount']
            self.rows = []
            for row in inner_params[u'rows']:
                self.rows.append(ResultRow(row))

        self.error_message = error_message


class ResultRow:
    def __init__(self, parameter):
        self.result_cells = []
        for result_cell in parameter:
            self.result_cells.append(ResultCell(result_cell))


class ResultCell:
    def __init__(self, parameter):
        self.display_value = parameter[u'displayValue']
        self.row_id = parameter[u'rowId']
        self.is_null = parameter[u'isNull']
