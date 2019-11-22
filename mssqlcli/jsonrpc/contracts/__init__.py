# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import logging
import abc

ABC = abc.ABCMeta('ABC', (object,), {})  # compatibile with Python 2 *and* 3.


class Request(ABC):
    """
        Abstract request class.
    """

    def __init__(self, request_id, owner_uri, finished, json_rpc_client, parameters):
        self.request_id = request_id
        self.owner_uri = owner_uri
        self.finished = finished
        self.json_rpc_client = json_rpc_client
        self.params = parameters

    @abc.abstractmethod
    def execute(self):
        """
            Executes the request.
        """

    @abc.abstractmethod
    def get_response(self):
    # def get_response(self, request_id, owner_uri, ConnectionCompleteEvent, decode_response):
        """
            Retrieves expected response.
        """
        # response = self.json_rpc_client.get_response(request_id, owner_uri)
        # decoded_response = None
        # if response:
        #     logger.debug(response)
        #     decoded_response = self.decode_response(response)

        # if isinstance(decoded_response, ConnectionCompleteEvent):
        #     self.finished = True
        #     self.json_rpc_client.request_finished(self.request_id)
        #     self.json_rpc_client.request_finished(self.owner_uri)

        # return decoded_response

    @abc.abstractmethod
    def completed(self):
        """
            Return state of request.
        """
