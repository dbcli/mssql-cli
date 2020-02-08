# coding=utf-8
import tempfile
import json
import os
import unittest
from stat import ST_MTIME

import mssqlcli.telemetry_upload as telemetry_upload


try:
    # Python 2.x
    from urllib2 import HTTPError
except ImportError:
    # Python 3.x
    from urllib.error import HTTPError


class TelemetryTests(unittest.TestCase):
    """
        Tests for telemetry client.
    """
    @staticmethod
    def build_telemetry_client():
        import mssqlcli.telemetry as telemetry      # pylint: disable=import-outside-toplevel
        return telemetry

    @unittest.skipUnless(os.environ['MSSQL_CLI_TELEMETRY_OPTOUT'].lower() != 'true',
                         "Only works when telemetry opt-out not set to true.")
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
                self.assertTrue(prop in expected_data_model_properties,
                                'Additional property detected: {}.'.format(prop))

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

    def test_file_time_check_rotation(self):
        test_telemetry_client = self.build_telemetry_client()
        expired_id_file = tempfile.NamedTemporaryFile()
        valid_id_file = tempfile.NamedTemporaryFile()
        try:
            st = os.stat(expired_id_file.name)
            modified_time = st[ST_MTIME]
            older_modified_time = modified_time - (25 * 3600)
            # Update modified time.
            os.utime(expired_id_file.name, (modified_time, older_modified_time))

            # Verify both scenarios of a valid and expired id file.
            # pylint: disable=protected-access
            self.assertTrue(test_telemetry_client._user_id_file_is_old(expired_id_file.name))
            self.assertFalse(test_telemetry_client._user_id_file_is_old(valid_id_file.name))
        finally:
            expired_id_file.close()
            valid_id_file.close()


if __name__ == u'__main__':
    # Enabling this env var would output what telemetry payload is sent.
    os.environ[telemetry_upload.DIAGNOSTICS_TELEMETRY_ENV_NAME] = 'False'
    unittest.main()
