# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import io
import unittest
import pgcli.jsonrpc.jsonrpcclient as jsonrpc


class JsonRpcTest(unittest.TestCase):
    """
        Json Rpc tests.
    """

    def test_basic_response(self):
        """
            Verify json rpc reader can read a valid response.
        """
        test_stream = io.BytesIO(b'Content-Length: 15\r\n\r\n{"key":"value"}')
        json_rpc_reader = jsonrpc.JsonRpcReader(test_stream)
        response = json_rpc_reader.read_response()
        baseline = {u'key': u'value'}
        self.assertEqual(response, baseline)

        json_rpc_reader.close()
        self.assertTrue(test_stream.closed)

    def test_basic_request(self):
        """
            Verify json rpc writer submits a valid request.
        """
        test_stream = io.BytesIO()
        json_rpc_writer = jsonrpc.JsonRpcWriter(test_stream)
        json_rpc_writer.send_request(
            method=u'testMethod/DoThis',
            params={
                u'Key': u'Value'},
            id=1)

        # Use JSON RPC reader to read request.
        test_stream.seek(0)
        json_rpc_reader = jsonrpc.JsonRpcReader(test_stream)
        response = json_rpc_reader.read_response()
        baseline = {
            u'jsonrpc': u'2.0',
            u'params': {
                u'Key': u'Value'},
            u'method': u'testMethod/DoThis',
            u'id': 1}
        self.assertEqual(response, baseline)

        json_rpc_reader.close()
        self.assertTrue(test_stream.closed)

    def test_nested_request(self):
        """
            Verify submission of a valid nested request.
        """
        test_stream = io.BytesIO()
        json_rpc_writer = jsonrpc.JsonRpcWriter(test_stream)
        json_rpc_writer.send_request(
            method=u'testMethod/DoThis',
            params={
                u'Key': u'Value',
                u'key2': {
                    u'key3': u'value3',
                    u'key4': u'value4'}},
            id=1)

        test_stream.seek(0)
        json_rpc_reader = jsonrpc.JsonRpcReader(test_stream)
        response = json_rpc_reader.read_response()
        baseline = {
            u'jsonrpc': u'2.0',
            u'params': {
                u'Key': u'Value',
                u'key2': {
                    u'key3': u'value3',
                    u'key4': u'value4'}},
            u'method': u'testMethod/DoThis',
            u'id': 1}
        self.assertEqual(response, baseline)

        json_rpc_reader.close()
        self.assertTrue(test_stream.closed)

    def test_response_multiple_headers(self):
        """
            Verify json rpc reader can read response with multiple headers.
        """
        test_stream = io.BytesIO(
            b'Content-Length: 15\r\nHeader2: content2\r\nHeader3: content3\r\n\r\n{"key":"value"}')
        json_rpc_reader = jsonrpc.JsonRpcReader(test_stream)
        response = json_rpc_reader.read_response()
        baseline = {u'key': u'value'}
        self.assertEqual(response, baseline)

        json_rpc_reader.close()
        self.assertTrue(test_stream.closed)

    def test_incorrect_header_formats(self):
        """
            Assert expected exception when reading response with invalid headers.
        """
        # Verify end of stream thrown with invalid header.
        test_stream = io.BytesIO(b'Content-Length: 15\r\n{"key":"value"}')
        json_rpc_reader = jsonrpc.JsonRpcReader(test_stream)
        with self.assertRaises(EOFError):
            json_rpc_reader.read_response()

        # Test with no content-length header.
        test_stream = io.BytesIO(b'Missing-Header: True\r\n\r\n')
        json_rpc_reader = jsonrpc.JsonRpcReader(test_stream)
        with self.assertRaises(LookupError):
            json_rpc_reader.read_response()

        json_rpc_reader.close()
        self.assertTrue(test_stream.closed)

        # Missing colon.
        test_stream = io.BytesIO(b'Retry-On-Failure True\r\n\r\n')
        json_rpc_reader = jsonrpc.JsonRpcReader(test_stream)
        with self.assertRaises(KeyError):
            json_rpc_reader.read_response()
        json_rpc_reader.close()
        self.assertTrue(test_stream.closed)

    def test_invalid_json_response(self):
        """
            Assert expected exception reading response with invalid json.
        """
        # Verify error thrown with invalid JSON.
        test_stream = io.BytesIO(b'Content-Length: 14\r\n\r\n{"key":"value"')
        json_rpc_reader = jsonrpc.JsonRpcReader(test_stream)
        with self.assertRaises(ValueError):
            json_rpc_reader.read_response()

    def test_invalid_content_length_value_response(self):
        """
            Assert expected exception reading response with invalid content length value.
        """
        # Verify error thrown with invalid content length value.
        test_stream = io.BytesIO(b'Content-Length: X\r\n\r\n{"key":"value"}')
        json_rpc_reader = jsonrpc.JsonRpcReader(test_stream)
        with self.assertRaises(ValueError):
            json_rpc_reader.read_response()

    def test_stream_closes_during_read_and_write(self):
        """
            Assert expected exception on attempt to read and write to a closed stream.
        """
        test_stream = io.BytesIO()
        json_rpc_writer = jsonrpc.JsonRpcWriter(test_stream)
        json_rpc_writer.send_request(
            method=u'testMethod/DoThis',
            params={
                u'Key': u'Value'},
            id=1)

        # reset the stream.
        test_stream.seek(0)
        json_rpc_reader = jsonrpc.JsonRpcReader(test_stream)

        test_stream.close()
        with self.assertRaises(ValueError):
            json_rpc_reader.read_response()

        test_stream = io.BytesIO()
        json_rpc_writer = jsonrpc.JsonRpcWriter(test_stream)
        test_stream.close()

        with self.assertRaises(ValueError):
            json_rpc_writer.send_request(
                method=u'testMethod/DoThis',
                params={
                    u'Key': u'Value'},
                id=1)

    def test_trigger_buffer_resize(self):
        """
            Verify buffer resize trigger.
        """
        test_stream = io.BytesIO(b'Content-Length: 15\r\n\r\n{"key":"value"}')
        json_rpc_reader = jsonrpc.JsonRpcReader(test_stream)
        # set the message buffer to a small size triggering a resize.
        json_rpc_reader.buffer = bytearray(2)
        # Initial size set to 2 bytes.
        self.assertEqual(len(json_rpc_reader.buffer), 2)
        response = json_rpc_reader.read_response()
        baseline = {u'key': u'value'}
        self.assertEqual(response, baseline)
        # Verify message buffer was reset to it's default max size.
        self.assertEqual(len(json_rpc_reader.buffer), 8192)

    def test_max_buffer_resize(self):
        """
            Verify max buffer resize.
        """
        test_stream = io.BytesIO(b'Content-Length: 15\r\n\r\n{"key":"value"}')
        json_rpc_reader = jsonrpc.JsonRpcReader(test_stream)
        # Double buffer size to max to verify resize takes leftover size.
        json_rpc_reader.buffer = bytearray(16384)
        # Verify initial buffer size was set.
        self.assertEqual(len(json_rpc_reader.buffer), 16384)
        response = json_rpc_reader.read_response()
        baseline = {u'key': u'value'}
        self.assertEqual(response, baseline)
        # Verify buffer size decreased by bytes_read.
        self.assertEqual(len(json_rpc_reader.buffer), 16347)

    def test_read_state(self):
        """
            Assert read states are valid.
        """
        test_stream = io.BytesIO(b'Content-Length: 15\r\n\r\n')
        json_rpc_reader = jsonrpc.JsonRpcReader(test_stream)
        self.assertEqual(json_rpc_reader.read_state, jsonrpc.ReadState.Header)

        json_rpc_reader.read_next_chunk()
        header_read = json_rpc_reader.try_read_headers()

        self.assertTrue(header_read)
        self.assertEqual(json_rpc_reader.read_state, jsonrpc.ReadState.Content)

    def test_case_insensitive_header(self):
        """
            Verify case insensitivty when reading headers.
        """
        test_stream = io.BytesIO(b'CONTENT-LENGTH: 15\r\n\r\n{"key":"value"}')
        json_rpc_reader = jsonrpc.JsonRpcReader(test_stream)
        response = json_rpc_reader.read_response()
        baseline = {u'key': u'value'}
        self.assertEqual(response, baseline)

        test_stream = io.BytesIO(b'CoNtEnT-lEngTh: 15\r\n\r\n{"key":"value"}')
        json_rpc_reader = jsonrpc.JsonRpcReader(test_stream)
        response = json_rpc_reader.read_response()
        baseline = {u'key': u'value'}
        self.assertEqual(response, baseline)


if __name__ == u'__main__':
    unittest.main()
