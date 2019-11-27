# pylint: disable=too-many-arguments
import logging
import abc

ABC = abc.ABCMeta('ABC', (object,), {})  # compatibile with Python 2 *and* 3.
logger = logging.getLogger(u'mssqlcli.connectionservice')

class Request(ABC):
    """
        Abstract request class.
    """

    def __init__(self, request_id, owner_uri, json_rpc_client, parameters,
                 method_name, connectionCompleteEvent):
        self.request_id = request_id
        self.owner_uri = owner_uri
        self.json_rpc_client = json_rpc_client
        self.params = parameters
        self.method_name = method_name
        self.connectionCompleteEvent = connectionCompleteEvent
        self.finished = False

    @staticmethod
    @abc.abstractmethod
    def decode_response(response):
        """
            Returns decoded response.
        """
        pass

    @classmethod
    @abc.abstractmethod
    def response_error(cls, error):
        """
            Returns object when response fails.
        """
        pass

    def execute(self):
        """
            Executes the request.
        """
        self.json_rpc_client.submit_request(
            self.method_name, self.params.format(), self.request_id)

    def get_response(self):
        """
            Get latest response, event or exception if it occured.
        """
        try:
            response = self.json_rpc_client.get_response(self.request_id, self.owner_uri)
            decoded_response = None
            if response:
                logger.debug(response)
                decoded_response = self.decode_response(response)

            if isinstance(decoded_response, self.connectionCompleteEvent):
                self.finished = True
                self.json_rpc_client.request_finished(self.request_id)
                self.json_rpc_client.request_finished(self.owner_uri)
            return decoded_response
        except Exception as error:  # pylint: disable=broad-except
            logger.info(str(error))
            self.finished = True
            self.json_rpc_client.request_finished(self.request_id)
            self.json_rpc_client.request_finished(self.owner_uri)
            return self.response_error(error)

    def completed(self):
        """
            Return state of request.
        """
        return self.finished
