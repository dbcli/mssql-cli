# pylint: disable=too-many-instance-attributes
# pylint: disable=too-few-public-methods

from mssqlcli.jsonrpc.contracts import Request


class ConnectionRequest(Request):
    """
        SqlToolsService Connection request.
    """

    def __init__(self, request_id, owner_uri, json_rpc_client, parameters):
        super(ConnectionRequest, self).__init__(request_id, owner_uri, json_rpc_client,
                                                ConnectionParams(parameters),
                                                u'connection/connect',
                                                ConnectionCompleteEvent)

    @classmethod
    def response_error(cls, error):
        return ConnectionCompleteEvent({
            u'params': {
                u'ownerUri': cls.owner_uri,
                u'connectionId': None,
                u'messages': str(error),
                u'errorMessage': u'Connection request encountered an exception',
                u'errorNumber': None
            }
        })

    @staticmethod
    def decode_response(response):
        """
            Decode response dictionary into a Connection parameter type.
        """

        if u'result' in response:
            return ConnectionResponse(response)

        if 'method' in response and response['method'] == 'connection/complete':
            return ConnectionCompleteEvent(response)

        # Could not decode return st
        return response


class ConnectionDetails:
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


class ConnectionParams:
    def __init__(self, parameters):
        self.owner_uri = parameters[u'OwnerUri']
        self.connection_details = ConnectionDetails(parameters)

    def format(self):
        return {u'OwnerUri': self.owner_uri,
                u'Connection': self.connection_details.format()}


#
#   The Connection Events.
#

class ConnectionCompleteEvent:
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

        if u'connectionSummary' in inner_params and inner_params[u'connectionSummary']:
            self.connected_database = inner_params[u'connectionSummary'][u'databaseName']


class ConnectionResponse:
    def __init__(self, params):
        self.result = params[u'result']
        self.request_id = params[u'id']
