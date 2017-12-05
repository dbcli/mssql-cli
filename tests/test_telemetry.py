# coding=utf-8
import json
import os
import unittest

import mssqlcli.telemetry_upload as telemetry_upload

try:
    # Python 2.x
    import urllib2 as HTTPClient
    from urllib2 import HTTPError
except ImportError:
    # Python 3.x
    import urllib.request as HTTPClient
    from urllib.error import HTTPError


class TelemetryTests(unittest.TestCase):
    """
        Tests for telemetry client.
    """
    @staticmethod
    def build_telemetry_client():
        import mssqlcli.telemetry as telemetry
        return telemetry

    def test_telemetry_data_points(self):
        test_telemetry_client = self.build_telemetry_client()
        test_telemetry_client.start()

        try:
            payload = test_telemetry_client.conclude(
                                        service_endpoint_uri='https://vortex.data.microsoft.com/collect/v1/validate',
                                        separate_process=False)
            self.assertIsNotNone(payload, 'Payload was empty.')
        except HTTPError:
            self.fail('Recevied HTTP Error when validating payload against vortex.')

        payload = json.loads(payload.replace("'", '"'))

        expected_data_model_properties = [
                'Reserved.ChannelUsed',
                'Reserved.SequenceNumber',
                'Reserved.EventId',
                'Reserved.SessionId',
                'Reserved.TimeSinceSessionStart',
                'Reserved.DataModel.Source',
                'Reserved.DataModel.EntitySchemaVersion',
                'Reserved.DataModel.Severity',
                'Reserved.DataModel.CorrelationId',
                'Context.Default.SQLTools.ExeName',
                'Context.Default.SQLTools.ExeVersion',
                'Context.Default.SQLTools.MacAddressHash',
                'Context.Default.SQLTools.OS.Type',
                'Context.Default.SQLTools.OS.Version',
                'Context.Default.SQLTools.IsDocker',
                'Context.Default.SQLTools.User.Id',
                'Context.Default.SQLTools.User.IsMicrosoftInternal',
                'Context.Default.SQLTools.User.IsOptedIn',
                'Context.Default.SQLTools.ShellType',
                'Context.Default.SQLTools.EnvironmentVariables',
                'Context.Default.SQLTools.Locale',
                'Context.Default.SQLTools.StartTime',
                'Context.Default.SQLTools.EndTime',
                'Context.Default.SQLTools.SessionDuration',
                'Context.Default.SQLTools.PythonVersion',
                'Context.Default.SQLTools.ServerVersion',
                'Context.Default.SQLTools.ServerEdition',
                'Context.Default.SQLTools.ConnectionType',
        ]

        for record in payload:
            properties = record['properties']
            for prop in properties:
                self.assertTrue(prop in expected_data_model_properties, 'Additional property detected: {}.'.format(prop))

    def test_telemetry_vortex_format(self):
        test_telemetry_client = self.build_telemetry_client()
        test_telemetry_client.start()

        os.environ[test_telemetry_client.MSSQL_CLI_TELEMETRY_OPT_OUT] = 'False'
        try:
            payload = test_telemetry_client.conclude(
                                        service_endpoint_uri='https://vortex.data.microsoft.com/collect/v1/validate',
                                        separate_process=False)
            self.assertIsNotNone(payload, 'Payload was empty.')
        except HTTPError:
            self.fail('Recevied HTTP Error when validating payload against vortex.')

    def test_telemetry_opt_out(self):
        test_telemetry_client = self.build_telemetry_client()
        os.environ[test_telemetry_client.MSSQL_CLI_TELEMETRY_OPT_OUT] = 'True'

        test_telemetry_client.start()
        payload = test_telemetry_client.conclude()
        self.assertIsNone(payload, 'Payload was uploaded when client opted out.')


if __name__ == u'__main__':
    # Enabling this env var would output what telemetry payload is sent.
    os.environ[telemetry_upload.DIAGNOSTICS_TELEMETRY_ENV_NAME] = 'False'
    unittest.main()
