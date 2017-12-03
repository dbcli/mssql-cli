# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
import time
import io

import mssqlcli.jsonrpc.jsonrpcclient as json_rpc_client


class JsonRpcClientTests(unittest.TestCase):
    """
        Json Rpc client tests.
    """

    def test_request_enqueued(self):
        """
            Verify requests are enqueued.
        """
        input_stream = io.BytesIO()
        output_stream = io.BytesIO(b'sample output')

        test_client = json_rpc_client.JsonRpcClient(
            input_stream, output_stream)
        test_client.submit_request(
            u'scriptingService/ScriptDatabase', {u'ScriptDatabaseOptions': u'True'})

        test_client = json_rpc_client.JsonRpcClient(
            input_stream, output_stream)
        test_client.submit_request(
            u'scriptingService/ScriptDatabase', {u'ScriptDatabaseOptions': u'True'})

        request = test_client.request_queue.get()

        self.assertEqual(
            request[u'method'],
            u'scriptingService/ScriptDatabase')
        self.assertEqual(
            request[u'params'], {
                u'ScriptDatabaseOptions': u'True'})

    def test_response_dequeued(self):
        """
            Verify response was read.
        """
        input_stream = io.BytesIO()
        output_stream = io.BytesIO(
            b'Content-Length: 15\r\n\r\n{"key":"value"}')

        test_client = json_rpc_client.JsonRpcClient(
            input_stream, output_stream)
        test_client.start()
        time.sleep(.2)
        response = test_client.get_response()
        baseline = {u'key': u'value'}

        self.assertEqual(response, baseline)
        self.shutdown_background_threads(test_client)
        # All background threads should be shut down.
        self.assertFalse(test_client.request_thread.isAlive())
        self.assertFalse(test_client.response_thread.isAlive())

    def test_submit_simple_request(self):
        """
            Verify simple request submitted.
        """
        input_stream = io.BytesIO()
        output_stream = io.BytesIO(
            b'Content-Length: 15\r\n\r\n{"key":"value"}')

        test_client = json_rpc_client.JsonRpcClient(
            input_stream, output_stream)
        test_client.start()
        time.sleep(.5)
        # Verify threads are alive and running.
        self.assertTrue(test_client.request_thread.isAlive())
        self.assertFalse(test_client.response_thread.isAlive())

        test_client.submit_request(
            u'scriptingService/ScriptDatabase', {u'ScriptDatabaseOptions': u'True'})

        self.shutdown_background_threads(test_client)

        # check stream contents.
        input_stream.seek(0)
        expected = b'Content-Length: 120\r\n\r\n{"id": null, "jsonrpc": "2.0", "method": "scriptingService/ScriptDatabase", "params": {"ScriptDatabaseOptions": "True"}}'

        self.assertEqual(input_stream.getvalue(), expected)
        self.assertFalse(test_client.request_thread.isAlive())
        self.assertFalse(test_client.response_thread.isAlive())

    def test_send_multiple_request(self):
        """
            Verifies we can successfully submit multiple requests.
        """
        input_stream = io.BytesIO()
        output_stream = io.BytesIO(
            b'Content-Length: 15\r\n\r\n{"key":"value"}')

        test_client = json_rpc_client.JsonRpcClient(
            input_stream, output_stream)
        test_client.start()
        time.sleep(.5)
        # request thread is alive.
        # response thread is dead due to reaching EOF.
        self.assertTrue(test_client.request_thread.isAlive())
        self.assertFalse(test_client.response_thread.isAlive())

        test_client.submit_request(
            u'scriptingService/ScriptDatabase', {u'ScriptDatabaseOptions': u'True'})
        test_client.submit_request(
            u'scriptingService/ScriptDatabase', {u'ScriptCollations': u'True'})
        test_client.submit_request(
            u'scriptingService/ScriptDatabase', {u'ScriptDefaults': u'True'})

        # Minimum sleep time for main thread, so background threads can process
        # the requests.
        time.sleep(1)

        # Kill the threads so we can just verify the queues.
        self.shutdown_background_threads(test_client)

        input_stream.seek(0)
        expected = \
            b'Content-Length: 120\r\n\r\n{"id": null, "jsonrpc": "2.0", "method": "scriptingService/ScriptDatabase", "params": {"ScriptDatabaseOptions": "True"}}'\
            b'Content-Length: 115\r\n\r\n{"id": null, "jsonrpc": "2.0", "method": "scriptingService/ScriptDatabase", "params": {"ScriptCollations": "True"}}'\
            b'Content-Length: 113\r\n\r\n{"id": null, "jsonrpc": "2.0", "method": "scriptingService/ScriptDatabase", "params": {"ScriptDefaults": "True"}}'

        self.assertEqual(input_stream.getvalue(), expected)
        self.assertFalse(test_client.request_thread.isAlive())
        self.assertFalse(test_client.response_thread.isAlive())

    def test_normal_shutdown(self):
        """
            Verify normal shutdown.
        """
        input_stream = io.BytesIO()
        output_stream = io.BytesIO(
            b'Content-Length: 15\r\n\r\n{"key":"value"}')

        test_client = json_rpc_client.JsonRpcClient(
            input_stream, output_stream)
        test_client.start()
        time.sleep(.5)
        # Verify threads alive.
        self.assertTrue(test_client.request_thread.isAlive())

        # Response thread is dead due to EOF.
        self.assertFalse(test_client.response_thread.isAlive())

        test_client.shutdown()

        self.assertFalse(test_client.request_thread.isAlive())
        self.assertFalse(test_client.response_thread.isAlive())

    def test_send_invalid_request(self):
        """
            Verifies that a request with a null method or parameter is not enqueued.
        """
        input_stream = io.BytesIO()
        output_stream = io.BytesIO(b'sample output')

        test_client = json_rpc_client.JsonRpcClient(
            input_stream, output_stream)
        with self.assertRaises(ValueError):
            test_client.submit_request(None, None)

    def test_receive_invalid_response_exception(self):
        """
            Verify invalid response has exception queued and response thread dies.
        """
        input_stream = io.BytesIO()
        output_stream = io.BytesIO(b'Cntent-Lenth:15\r\n\r\n')

        test_client = json_rpc_client.JsonRpcClient(
            input_stream, output_stream)
        test_client.start()

        try:
            # Retrieve the latest response or earliest exception.
            test_client.get_response()
        except LookupError as exception:
            # Verify the background thread communicated the exception.
            self.assertEqual(
                str(exception),
                u'Content-Length was not found in headers received.')
            # Lookup exception for invalid content length spelling.
            self.assertTrue(test_client.request_thread.isAlive())
            self.assertFalse(test_client.response_thread.isAlive())
            test_client.shutdown()
            self.assertFalse(test_client.request_thread.isAlive())

    def test_response_stream_closed_exception(self):
        """
            Verify response stream closed, exception returned and response thread died.
        """
        input_stream = io.BytesIO()
        output_stream = io.BytesIO(b'Content-Lenth:15\r\n\r\n')
        output_stream.close()

        test_client = json_rpc_client.JsonRpcClient(
            input_stream, output_stream)
        test_client.start()

        try:
            test_client.get_response()
        except ValueError as exception:
            # Verify the background thread communicated the exception.
            self.assertEqual(
                str(exception), u'I/O operation on closed file.')

            self.assertTrue(test_client.request_thread.isAlive())
            self.assertFalse(test_client.response_thread.isAlive())
            test_client.shutdown()
            self.assertFalse(test_client.request_thread.isAlive())

    @unittest.skip("Disabling until scenario is valid")
    def test_stream_has_no_response(self):
        """
            Verify response thread is alive while output stream has no output.
        """
        input_stream = io.BytesIO()
        output_stream = io.BytesIO()

        test_client = json_rpc_client.JsonRpcClient(
            input_stream, output_stream)
        test_client.start()
        response = test_client.get_response()

        self.assertEqual(response, None)
        self.assertTrue(test_client.request_thread.isAlive())
        self.assertTrue(test_client.response_thread.isAlive())
        test_client.shutdown()
        self.assertFalse(test_client.request_thread.isAlive())
        self.assertFalse(test_client.response_thread.isAlive())

    def test_stream_closed_during_process(self):
        """
            Verify request stream closed, exception returned and request thread died.
        """
        input_stream = io.BytesIO()
        output_stream = io.BytesIO(
            b'Content-Length: 15\r\n\r\n{"key":"value"}')

        test_client = json_rpc_client.JsonRpcClient(
            input_stream, output_stream)
        test_client.start()
        input_stream.close()
        test_client.submit_request(
            'scriptingService/ScriptDatabase', {'ScriptLogins': 'True'})
        # sleep 1 second for request thread to process.
        time.sleep(1)

        try:
            test_client.get_response()
        except ValueError as exception:
            # Verify the background thread communicated the exception.
            self.assertEqual(
                str(exception), u'I/O operation on closed file.')
            # Verify response thread is dead.
            self.assertFalse(test_client.request_thread.isAlive())
            test_client.shutdown()

    def test_get_response_with_id(self):
        """
            Verify response retrieval with id returns global event or response.
        """
        input_stream = io.BytesIO()
        output_stream = io.BytesIO(
            b'Content-Length: 86\r\n\r\n{"params": {"Key": "Value"}, "jsonrpc": "2.0", "method": "testMethod/DoThis", "id": 1}')

        test_client = json_rpc_client.JsonRpcClient(
            input_stream, output_stream)
        test_client.start()

        # Sleeping to give background threads a chance to process response.
        time.sleep(1)

        # Sleeping to give background threads a chance to process response.
        time.sleep(1)

        baseline = {
            u'jsonrpc': u'2.0',
            u'params': {
                u'Key': u'Value'},
            u'method': u'testMethod/DoThis',
            u'id': 1}
        response = test_client.get_response(id=1)
        self.assertEqual(response, baseline)
        test_client.shutdown()

    def shutdown_background_threads(self, test_client):
        """
            Stops background leaves streams open for testing
        """
        test_client.cancel = True
        test_client.request_queue.put(None)

        test_client.request_thread.join()
        test_client.response_thread.join()


if __name__ == u'__main__':
    unittest.main()
