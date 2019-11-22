# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import logging
import abc

ABC = abc.ABCMeta('ABC', (object,), {})  # compatibile with Python 2 *and* 3.
logger = logging.getLogger(u'mssqlcli.connectionservice')

class Request(ABC):
    """
        Abstract request class.
    """

    def __init__(self, request_id, owner_uri, finished, json_rpc_client, parameters,
                 connectionCompleteEvent):
        self.request_id = request_id
        self.owner_uri = owner_uri
        self.finished = finished
        self.json_rpc_client = json_rpc_client
        self.params = parameters
        self.connectionCompleteEvent = connectionCompleteEvent

    @abc.abstractmethod
    def execute(self):
        """
            Executes the request.
        """

    @abc.abstractmethod
    def get_response(self):
        """
            Retrieves expected response.
        """

    def get_decoded_response(self, decode_response_method):
        """
            Retreives decoded response given a decoder.
        """
        response = self.json_rpc_client.get_response(self.request_id, self.owner_uri)
        decoded_response = None
        if response:
            logger.debug(response)
            decoded_response = decode_response_method(response)

        if isinstance(decoded_response, self.connectionCompleteEvent):
            self.finished = True
            self.json_rpc_client.request_finished(self.request_id)
            self.json_rpc_client.request_finished(self.owner_uri)

        return decoded_response

    @abc.abstractmethod
    def completed(self):
        """
            Return state of request.
        """
