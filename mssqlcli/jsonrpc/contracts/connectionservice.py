# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from mssqlcli.jsonrpc.contracts import Request

import sys
import logging

logger = logging.getLogger(u'mssqlcli.connectionservice')


class ConnectionRequest(Request):
    """
        SqlToolsService Connection request.
    """
    METHOD_NAME = u'connection/connect'

    def __init__(self, id, json_rpc_client, parameters):
        self.id = id
        self.finished = False
        self.json_rpc_client = json_rpc_client
        self.params = ConnectionParams(parameters)

    def execute(self):
        self.json_rpc_client.submit_request(
            self.METHOD_NAME, self.params.format(), self.id)

    def get_response(self):
        """
            Get latest response, event or exception if it occured.
        """
        try:
            response = self.json_rpc_client.get_response(self.id)
            decoded_response = None

            if response:
                logger.debug(response)
                decoded_response = self.decode_response(response)

            if isinstance(decoded_response, ConnectionCompleteEvent):
                self.finished = True
                self.json_rpc_client.request_finished(self.id)

            return decoded_response

        except Exception as error:
            logger.debug(str(error))
            self.finished = True
            self.json_rpc_client.request_finished(self.id)
            return ConnectionCompleteEvent({
                u'params': {
                    u'ownerUri': None,
                    u'connectionId': None,
                    u'messages': str(error),
                    u'errorMessage': u'Connection request encountered an exception',
                    u'errorNumber': None
                }
            })

    def completed(self):
        """
            Get current request state.
        """
        return self.finished

    def decode_response(self, obj):
        """
            Decode response dictionary into a Connection parameter type.
        """

        if u'result' in obj:
            return ConnectionResponse(obj)

        elif u'params' in obj:
            return ConnectionCompleteEvent(obj)

        # Could not decode return st
        return obj


class ConnectionDetails(object):
    """
        Connection details params.
    """

    def __init__(self, parameters):
        self.ServerName = parameters[u'ServerName']
        self.DatabaseName = parameters[u'DatabaseName']
        self.UserName = parameters[u'UserName']
        self.Password = parameters[u'Password']
        self.AuthenticationType = parameters[u'AuthenticationType']
        self.MultipleActiveResultSets = parameters[u'MultipleActiveResultSets']

    def format(self):
        return vars(self)


class ConnectionParams(object):
    def __init__(self, parameters):
        self.owner_uri = parameters['OwnerUri']
        self.connection_details = ConnectionDetails(parameters)

    def format(self):
        return {u'OwnerUri': self.owner_uri,
                u'Connection': self.connection_details.format()}


#
#   The Connection Events.
#

class ConnectionCompleteEvent(object):
    def __init__(self, params):
        inner_params = params[u'params']
        self.owner_uri = inner_params[u'ownerUri']
        self.connection_id = inner_params[u'connectionId']
        self.messages = inner_params[u'messages']
        self.error_message = inner_params[u'errorMessage']
        self.error_number = inner_params[u'errorNumber']


class ConnectionResponse(object):
    def __init__(self, params):
        self.result = params[u'result']
        self.id = params[u'id']


#
#   Handle Connection Events.
#

def handle_connection_response(response):
    # Handles complete notification and return ConnectionCompleteEvent object if connection successful.
    def handle_connection_complete_notification(response):
        if not response.connection_id:
            sys.stderr.write(u'\nConnection did not succeed.')
            if response.error_message:
                sys.stderr.write(u'\nError message: ' + response.error_message)
                logger.error(response.error_message)
            if response.messages:
                logger.error(response.messages)

        return response

    def handle_connection_response_notification(response):
        if response.result == False:
            sys.stderr.write(u'\nIncorrect json rpc request. Connection not successful.')
        return None

    response_handlers = {
        u'ConnectionResponse': handle_connection_response_notification,
        u'ConnectionCompleteEvent': handle_connection_complete_notification
    }

    response_name = type(response).__name__

    if response_name in response_handlers:
        return response_handlers[response_name](response)
