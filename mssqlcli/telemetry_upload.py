import datetime
import json
import os
import sys

from applicationinsights import TelemetryClient
from applicationinsights.channel import (
    TelemetryChannel, SynchronousQueue, SynchronousSender, contracts)
from applicationinsights.exceptions import enable

import mssqlcli.decorators as decorators

DIAGNOSTICS_TELEMETRY_ENV_NAME = 'MSSQL_CLI_DIAGNOSTICS_TELEMETRY'
INSTRUMENTATION_KEY = 'AIF-5574968e-856d-40d2-af67-c89a14e76412'

try:
    # Python 2.x
    import urllib2 as HTTPClient
    from urllib2 import HTTPError, URLError
except ImportError:
    # Python 3.x
    import urllib.request as HTTPClient
    from urllib.error import HTTPError, URLError


def in_diagnostic_mode():
    """
    When the telemetry runs in the diagnostic mode, exception are not suppressed and telemetry
    traces are dumped to the stdout.
    """
    return os.environ.get(DIAGNOSTICS_TELEMETRY_ENV_NAME, False) == 'True'


class VortexSynchronousSender(SynchronousSender):
    """
        A Synchronous sender specific to the Vortex service with limited retry logic.
    """
    def __init__(self, service_endpoint_uri='https://vortex.data.microsoft.com/collect/v1'):
        SynchronousSender.__init__(self, service_endpoint_uri)
        self.retry = 0

    def send(self, data_to_send):
        """
            Override the send method to strip the request_payload's brackets since Vortex does not.
        """
        request_payload = json.dumps([a.write() for a in data_to_send]).strip('[').strip(']')

        request = HTTPClient.Request(self._service_endpoint_uri,
                                     bytearray(request_payload, 'utf-8'),
                                     {'Accept': 'application/json',
                                      'Content-Type': 'application/json; charset=utf-8'})
        try:
            response = HTTPClient.urlopen(request, timeout=self._timeout)
            status_code = response.getcode()
            if 200 <= status_code < 300:
                if in_diagnostic_mode():
                    print('Telemetry uploaded succesfully.')
                return
        except HTTPError as e:
            if e.getcode() == 400:
                raise e
        except (AttributeError, ValueError, URLError):
            if self.retry < 3:
                self.retry += 1
            else:
                return

        # Add our unsent data back on to the queue
        for data in data_to_send:
            self._queue.put(data)


class VortexTelemetryChannel(TelemetryChannel):
    """
        A Vortext telemetry channel that suppresses the ingest header.
    """
    def __init__(self, context=None, queue=None):
        TelemetryChannel.__init__(self, context, queue)

    def write(self, data, context=None):
        """
            Enqueues the passed in data to the queue.
        """
        local_context = context or self._context
        if not local_context:
            raise Exception('Context was required but not provided')

        if not data:
            raise Exception('Data was required but not provided')

        envelope = contracts.Envelope()
        # The only difference in behavior from it's parent class is setting the flag below.
        # Suppress Vortex ingest header.
        envelope.flags = 0x200000
        envelope.name = data.ENVELOPE_TYPE_NAME
        envelope.time = datetime.datetime.utcnow().isoformat() + 'Z'
        envelope.ikey = local_context.instrumentation_key
        tags = envelope.tags
        for key, value in self._write_tags(local_context):
            tags[key] = value
        envelope.data = contracts.Data()
        envelope.data.base_type = data.DATA_TYPE_NAME
        if hasattr(data, 'properties') and local_context.properties:
            properties = data.properties
            if not properties:
                properties = {}
                data.properties = properties
            for key in local_context.properties:
                if key not in properties:
                    properties[key] = local_context.properties[key]
        envelope.data.base_data = data

        self._queue.put(envelope)


def build_vortex_telemetry_client(service_endpoint_uri):
    """
        Build vortex telemetry client.
    """
    vortex_sender = VortexSynchronousSender(service_endpoint_uri)
    sync_queue = SynchronousQueue(vortex_sender)
    channel = VortexTelemetryChannel(None, queue=sync_queue)

    client = TelemetryClient(INSTRUMENTATION_KEY, channel)

    enable(INSTRUMENTATION_KEY)
    return client


@decorators.suppress_all_exceptions(raise_in_diagnostics=True)
def upload(data_to_save, service_endpoint_uri):

    client = build_vortex_telemetry_client(service_endpoint_uri)

    if in_diagnostic_mode():
        sys.stdout.write('Telemetry upload begins\n')
        sys.stdout.write('Got data {}\n'.format(json.dumps(json.loads(data_to_save), indent=2)))

    try:
        data_to_save = json.loads(data_to_save.replace("'", '"'))
    except Exception as err:  # pylint: disable=broad-except
        if in_diagnostic_mode():
            sys.stdout.write('{}/n'.format(str(err)))
            sys.stdout.write('Raw [{}]/n'.format(data_to_save))

    for record in data_to_save:
        name = record['name']
        raw_properties = record['properties']
        properties = {}
        measurements = {}
        for k in raw_properties:
            v = raw_properties[k]

            # pylint: disable=undefined-variable
            # suppress warning for undefined variable, since `basestring` was dropped in python 3
            if isinstance(v, str if sys.version_info[0] >= 3 else basestring):
                properties[k] = v
            else:
                measurements[k] = v
        client.track_event(name, properties, measurements)

    try:
        client.flush()
        if in_diagnostic_mode():
            sys.stdout.write('\nTelemetry upload completes\n')

    except HTTPError as e:
        if in_diagnostic_mode():
            raise e


if __name__ == '__main__':
    # If user doesn't agree to upload telemetry, this scripts won't be executed.
    # The caller should control.
    decorators.is_diagnostics_mode = in_diagnostic_mode
    upload(sys.argv[1], sys.argv[2])
