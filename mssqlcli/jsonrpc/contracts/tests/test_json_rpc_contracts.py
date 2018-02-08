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
                  u'test_simple_query.txt'),
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

            request = connectionservice.ConnectionRequest(id=u'1',
                                                          owner_uri=owner_uri,
                                                          json_rpc_client=rpc_client,
                                                          parameters=parameters)
            self.verify_connection_service_response(request=request,
                                                    expected_response_event=1,
                                                    expected_complete_event=1)
            rpc_client.shutdown()

    def test_query_execute_response_AdventureWorks2014(self):
        """
           Verify a successful query execute response for "select * from HumanResources.Department"
        """
        with open(self.get_test_baseline(
                  u'test_simple_query.txt'),
                  u'r+b',
                  buffering=0) as response_file:
            request_stream = io.BytesIO()
            rpc_client = json_rpc_client.JsonRpcClient(in_stream=request_stream,
                                                       out_stream=response_file)
            rpc_client.start()
            # Submit a dummy request.
            owner_uri = u'connectionservicetest'
            parameters = {u'OwnerUri': owner_uri,
                          u'Query': "select * from HumanResources.Department"}
            request = queryservice.QueryExecuteStringRequest(id=2,
                                                             owner_uri=owner_uri,
                                                             json_rpc_client=rpc_client,
                                                             parameters=parameters)
            self.verify_query_service_response(request=request,
                                               expected_message_event=1,
                                               expected_complete_event=1,
                                               expected_batch_summaries=1,
                                               expected_result_set_summaries=1,
                                               expected_row_count=16)
            rpc_client.shutdown()

    def test_query_subset_response_AdventureWorks2014(self):
        """
            Test the retrieval of the actual rows for "select * from HumanResources.Department"
        """
        with open(self.get_test_baseline(
                  u'test_simple_query.txt'),
                  u'r+b',
                  buffering=0) as response_file:
            request_stream = io.BytesIO()
            rpc_client = json_rpc_client.JsonRpcClient(
                request_stream, response_file)
            rpc_client.start()
            # Submit a dummy request.
            owner_uri = u'connectionservicetest'
            parameters = {u'OwnerUri': u'connectionservicetest',
                          u'BatchIndex': 0,
                          u'ResultSetIndex': 0,
                          u'RowsStartIndex': 0,
                          u'RowCount': 16}
            request = queryservice.QuerySubsetRequest(id=u'3',
                                                      owner_uri=owner_uri,
                                                      json_rpc_client=rpc_client,
                                                      parameters=parameters)
            self.verify_query_service_response(request=request,
                                               expected_result_subsets=1,
                                               expected_row_count=16)
            rpc_client.shutdown()

    def test_query_retrieve_correct_response(self):
        """
            Verify a query execute request never retrieves query request responses for a different query.
        """
        with open(self.get_test_baseline(
                  u'test_query_retrieve_correct_response.txt'),
                  u'r+b',
                  buffering=0) as response_file:
            request_stream = io.BytesIO()
            rpc_client = json_rpc_client.JsonRpcClient(in_stream=request_stream,
                                                       out_stream=response_file)
            rpc_client.start()

            owner_uri = u'mismatchquerycompleteresponse_2'
            parameters = {u'OwnerUri': owner_uri,
                          u'Query': "select * from HumanResources.Department"}
            request = queryservice.QueryExecuteStringRequest(id=u'3',
                                                             owner_uri=owner_uri,
                                                             json_rpc_client=rpc_client,
                                                             parameters=parameters)

            # The baseline file contains responses for a different owner uri, which this request should not receive.
            # Receiving a query complete event with a error message indicates we did not retrieve a wrong event.
            self.verify_query_service_response(request=request,
                                               expected_complete_event=1,
                                               expected_error_count=1)

            rpc_client.shutdown()

    def test_malformed_query_AdventureWorks2014(self):
        """
            Verify a failed query execute response for "select * from [HumanResources.Department"
        """
        with open(self.get_test_baseline(
                  u'test_malformed_query.txt'),
                  u'r+b',
                  buffering=0) as response_file:
            request_stream = io.BytesIO()
            rpc_client = json_rpc_client.JsonRpcClient(in_stream=request_stream,
                                                       out_stream=response_file)
            rpc_client.start()
            # Submit a dummy request.
            owner_uri = u'connectionservicetest'
            parameters = {u'OwnerUri': owner_uri,
                          u'Query': "select * from [HumanResources.Department"}
            request = queryservice.QueryExecuteStringRequest(id=u'2',
                                                             owner_uri=owner_uri,
                                                             json_rpc_client=rpc_client,
                                                             parameters=parameters)
            self.verify_query_service_response(request=request,
                                               expected_error_count=1)
            rpc_client.shutdown()

    def verify_connection_service_response(self,
                                           request,
                                           expected_response_event=0,
                                           expected_complete_event=0):
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

        self.assertEqual(response_event, expected_response_event)
        self.assertEqual(complete_event, expected_complete_event)

    def verify_query_service_response(self,
                                      request,
                                      expected_message_event=0,
                                      expected_complete_event=0,
                                      expected_batch_summaries=0,
                                      expected_result_set_summaries=0,
                                      expected_result_subsets=0,
                                      expected_row_count=0,
                                      expected_error_count=0):
        # QueryExecuteString responses
        query_message_events = 0
        query_complete_events = 0
        query_batch_summaries = 0
        query_result_set_summaries = 0

        # QuerySubsetRequest responses
        query_result_subsets = 0

        query_row_count = 0
        query_error_events = 0

        request.execute()
        time.sleep(1)

        while not request.completed():
            response = request.get_response()
            if response:
                if isinstance(response, queryservice.QueryMessageEvent):
                    query_message_events += 1
                elif isinstance(response, queryservice.QueryExecuteErrorResponseEvent):
                    query_error_events += 1
                elif isinstance(response, queryservice.QueryCompleteEvent):
                    query_complete_events += 1
                    if hasattr(response, 'batch_summaries'):
                        query_batch_summaries = len(response.batch_summaries)
                        query_result_set_summaries = len(
                            response.batch_summaries[0].result_set_summaries)
                        query_row_count = response.batch_summaries[0].result_set_summaries[0].row_count
                    if hasattr(response, 'exception_message') and response.exception_message:
                        query_error_events += 1
                elif isinstance(response, queryservice.ResultSubset):
                    query_result_subsets += 1
                    query_row_count = len(response.rows)

        self.assertEqual(query_message_events, expected_message_event)
        self.assertEqual(query_complete_events, expected_complete_event)
        self.assertEqual(query_batch_summaries, expected_batch_summaries)
        self.assertEqual(query_result_set_summaries, expected_result_set_summaries)

        self.assertEqual(query_result_subsets, expected_result_subsets)

        self.assertEqual(query_row_count, expected_row_count)
        self.assertEqual(query_error_events, expected_error_count)

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
