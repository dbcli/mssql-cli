#!/usr/bin/env python
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import io
import mssqlcli.jsonrpc.contracts.connectionservice as connectionservice
import mssqlcli.jsonrpc.jsonrpcclient as json_rpc_client
import time
import unittest


class ConnectionServiceTests(unittest.TestCase):
    """
        ConnectionServiceTests.
    """

    def test_successful_connection_AdventureWorks2014(self):
        """
            Verify a successful connection response
        """

        with open(self.get_test_baseline(u'select_from_humanresources_department_adventureworks2014.txt'), u'r+b', buffering=0) as response_file:
            request_stream = io.BytesIO()
            rpc_client = json_rpc_client.JsonRpcClient(
                request_stream, response_file)
            rpc_client.start()
            # Submit a dummy request.
            parameters = {u'OwnerUri': u'connectionservicetest',
                            u'ServerName': u'bro-hb',
                            u'DatabaseName': u'AdventureWorks2014',
                            u'UserName': u'*',
                            u'Password': u'*',
                            u'AuthenticationType': u'Integrated',
                            u'MultipleActiveResultSets': True}

            request = connectionservice.ConnectionRequest(1, rpc_client, parameters)
            self.verify_success_response(request=request)
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
