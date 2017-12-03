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


class QuerySubsetTests(unittest.TestCase):
    """
        QuerySubsetTests.
    """

    def test_query_subset_response_AdventureWorks2014(self):
        """
            Test the retrieval of the actual rows for "select * from HumanResources.Department"
        """

        with open(self.get_test_baseline(u'select_from_humanresources_department_adventureworks2014.txt'), u'r+b', buffering=0) as response_file:
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

            request = queryservice.QuerySubsetRequest(3, rpc_client, parameters)
            self.verify_subset_response(request=request)
            rpc_client.shutdown()

    def verify_subset_response(self, request):
        result_subset = 0
        # The expected row count is 16
        row_count = 0
        request.execute()
        time.sleep(1)

        while not request.completed():
            response = request.get_response()
            if response:
                if isinstance(response, queryservice.ResultSubset):
                    result_subset += 1
                    row_count = len(response.rows)

        self.assertEqual(result_subset, 1)
        self.assertEqual(row_count, 16)

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
