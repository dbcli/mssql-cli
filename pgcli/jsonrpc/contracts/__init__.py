# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import abc

ABC = abc.ABCMeta('ABC', (object,), {})  # compatibile with Python 2 *and* 3.


class Request(ABC):
    """
        Abstract request class.
    """
    @abc.abstractmethod
    def execute(self):
        """
            Executes the request.
        """
        pass

    @abc.abstractmethod
    def get_response(self):
        """
            Retrieves expected response.
        """
        pass

    @abc.abstractmethod
    def completed(self):
        """
            Return state of request.
        """
        pass
