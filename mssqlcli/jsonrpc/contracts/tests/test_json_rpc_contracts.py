#!/usr/bin/env python
import io
import os
import time
import unittest
import mssqlcli.jsonrpc.contracts.connectionservice as connectionservice
import mssqlcli.jsonrpc.contracts.queryexecutestringservice as queryservice
import mssqlcli.jsonrpc.jsonrpcclient as json_rpc_client


class JSONRPCContractsTests(unittest.TestCase):
    """
        Tests for validating SQLToolsservice API via JSONRPC.
    """

    def test_successful_connection_AdventureWorks2014(self):
        """
            Verify a successful connection response
        """

        with open(self.get_test_baseline(
                  u'select_from_humanresources_department_adventureworks2014.txt'),
                  u'r+b',
                  buffering=0) as response_file:

            request_stream = io.BytesIO()
            rpc_client = json_rpc_client.JsonRpcClient(in_stream=request_stream,
                                                       out_stream=response_file)
            rpc_client.start()
            owner_uri = u'connectionservicetest'
            parameters = {u'OwnerUri': owner_uri,
                          u'ServerName': u'bro-hb',
                          u'DatabaseName': u'AdventureWorks2014',
                          u'UserName': u'*',
                          u'Password': u'*',
                          u'AuthenticationType': u'Integrated',
                          u'MultipleActiveResultSets': True}

            request = connectionservice.ConnectionRequest(id=1,
                                                          owner_uri=owner_uri,
                                                          json_rpc_client=rpc_client,
                                                          parameters=parameters)
            self.verify_success_response(request=request)
            rpc_client.shutdown()

    def test_query_execute_response_AdventureWorks2014(self):
        """
            Verify a successful query execute response for "select * from HumanResources.Department"
        """

        with open(self.get_test_baseline(
                  u'select_from_humanresources_department_adventureworks2014.txt'),
                  u'r+b',
                  buffering=0) as response_file:

            request_stream = io.BytesIO()
            rpc_client = json_rpc_client.JsonRpcClient(in_stream=request_stream,
                                                       out_stream=response_file)
            rpc_client.start()
            # Submit a dummy request.
            owner_uri = u'queryexecutetest'
            parameters = {u'OwnerUri': owner_uri,
                          u'Query': "select * from HumanResources.Department"}

            request = queryservice.QueryExecuteStringRequest(id=2,
                                                             owner_uri=owner_uri,
                                                             json_rpc_client=rpc_client,
                                                             parameters=parameters)
            self.verify_query_response(request=request,
                                       expected_message_event=1,
                                       expected_complete_event=1,
                                       expected_batch_summaries=1,
                                       expected_result_set_summaries=1,
                                       expected_row_count=16)
            rpc_client.shutdown()

    def test_malformed_query_AdventureWorks2014(self):
        """
            Verify a failed query execute response for "select * from [HumanResources.Department"
        """

        with open(self.get_test_baseline(
                  u'malformed_query_adventureworks2014.txt'),
                  u'r+b',
                  buffering=0) as response_file:

            request_stream = io.BytesIO()
            rpc_client = json_rpc_client.JsonRpcClient(in_stream=request_stream,
                                                       out_stream=response_file)
            rpc_client.start()
            # Submit a dummy request.
            owner_uri = u'malformedquerytest'
            parameters = {u'OwnerUri': owner_uri,
                          u'Query': "select * from [HumanResources.Department"}

            request = queryservice.QueryExecuteStringRequest(id=2,
                                                             owner_uri=owner_uri,
                                                             json_rpc_client=rpc_client,
                                                             parameters=parameters)
            self.verify_query_response(request=request,
                                       expected_error_count=1)
            rpc_client.shutdown()

    def test_query_subset_response_AdventureWorks2014(self):
        """
            Test the retrieval of the actual rows for "select * from HumanResources.Department"
        """

        with open(self.get_test_baseline(
                  u'select_from_humanresources_department_adventureworks2014.txt'),
                  u'r+b',
                  buffering=0) as response_file:

            request_stream = io.BytesIO()
            rpc_client = json_rpc_client.JsonRpcClient(
                request_stream, response_file)
            rpc_client.start()
            # Submit a dummy request.
            parameters = {u'OwnerUri': u'connectionservicetest',
                          u'BatchIndex': 0,
                          u'ResultSetIndex': 0,
                          u'RowsStartIndex': 0,
                          u'RowCount': 16}

            request = queryservice.QuerySubsetRequest(
                3, rpc_client, parameters)
            self.verify_subset_response(request=request)
            rpc_client.shutdown()

    def verify_success_response(self, request):
        response_event = 0
        complete_event = 0
        request.execute()
        time.sleep(1)

        while not request.completed():
            response = request.get_response()
            if response:
                if isinstance(response, connectionservice.ConnectionResponse):
                    response_event += 1
                elif isinstance(response, connectionservice.ConnectionCompleteEvent):
                    if response.connection_id:
                        complete_event += 1
                        self.assertTrue(connectionservice.handle_connection_response(response).connection_id,
                                        response.connection_id)

        self.assertEqual(response_event, 1)
        self.assertEqual(complete_event, 1)

    def get_test_baseline(self, file_name):
        """
        Helper method to get baseline file.
        """
        return os.path.abspath(
            os.path.join(
                os.path.abspath(__file__),
                u'..',
                u'baselines',
                file_name))


if __name__ == u'__main__':
    unittest.main()
