from mssqlcli.jsonrpc.contracts import Request

import logging

logger = logging.getLogger(u'mssqlcli.connectionservice')


class ConnectionRequest(Request):
    """
        SqlToolsService Connection request.
    """
    METHOD_NAME = u'connection/connect'

    def __init__(self, id, owner_uri, json_rpc_client, parameters):
        self.id = id
        self.owner_uri = owner_uri
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
            response = self.json_rpc_client.get_response(self.id, self.owner_uri)
            decoded_response = None
            if response:
                logger.debug(response)
                decoded_response = self.decode_response(response)

            if isinstance(decoded_response, ConnectionCompleteEvent):
                self.finished = True
                self.json_rpc_client.request_finished(self.id)
                self.json_rpc_client.request_finished(self.owner_uri)

            return decoded_response

        except Exception as error:
            logger.info(str(error))
            self.finished = True
            self.json_rpc_client.request_finished(self.id)
            self.json_rpc_client.request_finished(self.owner_uri)
            return ConnectionCompleteEvent({
                u'params': {
                    u'ownerUri': self.owner_uri,
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

        elif 'method' in obj and obj['method'] == 'connection/complete':
            return ConnectionCompleteEvent(obj)

        # Could not decode return st
        return obj


class ConnectionDetails(object):
    """
        Connection details params.
    """

    def __init__(self, parameters):
        # Required params
        self.ServerName = parameters[u'ServerName']
        self.DatabaseName = parameters[u'DatabaseName']
        self.UserName = parameters[u'UserName']
        self.Password = parameters[u'Password']
        self.AuthenticationType = parameters[u'AuthenticationType']
        # Optional Params
        if u'Encrypt' in parameters:
            self.Encrypt = parameters[u'Encrypt']
        if u'TrustServerCertificate' in parameters:
            self.TrustServerCertificate = parameters[u'TrustServerCertificate']
        if u'ConnectTimeout' in parameters:
            self.ConnectTimeout = parameters[u'ConnectTimeout']
        if u'ApplicationIntent' in parameters:
            self.ApplicationIntent = parameters[u'ApplicationIntent']
        if u'MultiSubnetFailover' in parameters:
            self.MultiSubnetFailover = parameters[u'MultiSubnetFailover']
        if u'PacketSize' in parameters:
            self.PacketSize = parameters[u'PacketSize']

    def format(self):
        return vars(self)


class ConnectionParams(object):
    def __init__(self, parameters):
        self.owner_uri = parameters[u'OwnerUri']
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
        # server information.
        if u'serverInfo' in inner_params and inner_params[u'serverInfo']:
            self.is_cloud = inner_params[u'serverInfo'][u'isCloud'] if \
                u'isCloud' in inner_params[u'serverInfo'] else False
            self.server_version = inner_params[u'serverInfo'][u'serverVersion'] if \
                u'serverVersion' in inner_params[u'serverInfo'] else None
            self.server_edition = inner_params[u'serverInfo'][u'serverEdition'] if \
                u'serverEdition' in inner_params[u'serverInfo'] else None


class ConnectionResponse(object):
    def __init__(self, params):
        self.result = params[u'result']
        self.id = params[u'id']
