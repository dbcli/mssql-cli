#!/usr/bin/env python
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import io
import mssqlcli.jsonrpc.contracts.queryexecutestringservice as queryservice
import mssqlcli.jsonrpc.jsonrpcclient as json_rpc_client
import time
import unittest


class QueryExecuteTests(unittest.TestCase):
    """
        QueryExecuteTests.
    """

    def test_query_execute_response_AdventureWorks2014(self):
        """
            Verify a successful query execute response for "select * from HumanResources.Department"
        """

        with open(self.get_test_baseline(u'select_from_humanresources_department_adventureworks2014.txt'), u'r+b', buffering=0) as response_file:
            request_stream = io.BytesIO()
            rpc_client = json_rpc_client.JsonRpcClient(
                request_stream, response_file)
            rpc_client.start()
            # Submit a dummy request.
            parameters = {u'OwnerUri': u'connectionservicetest',
                          u'Query': "select * from HumanResources.Department"}

            request = queryservice.QueryExecuteStringRequest(
                2, rpc_client, parameters)
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

        with open(self.get_test_baseline(u'malformed_query_adventureworks2014.txt'), u'r+b', buffering=0) as response_file:
            request_stream = io.BytesIO()
            rpc_client = json_rpc_client.JsonRpcClient(
                request_stream, response_file)
            rpc_client.start()
            # Submit a dummy request.
            parameters = {u'OwnerUri': u'connectionservicetest',
                          u'Query': "select * from [HumanResources.Department"}

            request = queryservice.QueryExecuteStringRequest(
                2, rpc_client, parameters)
            self.verify_query_response(request=request,
                                       expected_error_count=1)
            rpc_client.shutdown()

    def verify_query_response(self,
                              request,
                              expected_message_event=0,
                              expected_complete_event=0,
                              expected_batch_summaries=0,
                              expected_result_set_summaries=0,
                              expected_row_count=0,
                              expected_error_count=0):
        message_event = 0
        complete_event = 0
        batch_summaries = 0
        result_set_summaries = 0
        row_count = 0
        error_count = 0

        request.execute()
        time.sleep(1)

        while not request.completed():
            response = request.get_response()
            if response:
                if isinstance(response, queryservice.QueryMessageEvent):
                    message_event += 1
                elif isinstance(response, queryservice.QueryExecuteErrorResponseEvent):
                    error_count += 1
                elif isinstance(response, queryservice.QueryCompleteEvent):
                    complete_event += 1
                    if hasattr(response, 'batch_summaries'):
                        batch_summaries = len(response.batch_summaries)
                        result_set_summaries = len(
                            response.batch_summaries[0].result_set_summaries)
                        row_count = response.batch_summaries[0].result_set_summaries[0].row_count

        self.assertEqual(message_event, expected_message_event)
        self.assertEqual(complete_event, expected_complete_event)
        self.assertEqual(batch_summaries, expected_batch_summaries)
        self.assertEqual(result_set_summaries, expected_result_set_summaries)
        self.assertEqual(row_count, expected_row_count)
        self.assertEqual(error_count, expected_error_count)

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
