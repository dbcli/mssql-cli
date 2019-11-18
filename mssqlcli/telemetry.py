import binascii
import json
import locale
import os
import subprocess
import platform
import re
import sys
import traceback
import uuid
from functools import wraps
from datetime import datetime, timedelta
from mssqlcli import __version__ as mssql_cli_version
import mssqlcli.config as config
import mssqlcli.telemetry_upload as telemetry_core
import mssqlcli.decorators as decorators

PRODUCT_NAME = 'mssqlcli'
TELEMETRY_VERSION = '0.0.1'
MSSQL_CLI_TELEMETRY_FILE = 'mssqlcli_telemetry.log'
MSSQL_CLI_TELEMETRY_OPT_OUT = 'MSSQL_CLI_TELEMETRY_OPTOUT'
MSSQL_CLI_IN_DOCKER = 'MSSQL_CLI_IN_DOCKER'
MSSQL_CLI_TELEMETRY_ID_FILE = 'mssqlcli_telemetry_id.txt'

decorators.is_diagnostics_mode = telemetry_core.in_diagnostic_mode


def _user_agrees_to_telemetry(func):
    @wraps(func)
    def _wrapper(*args, **kwargs):
        user_opted_out = os.environ.get(MSSQL_CLI_TELEMETRY_OPT_OUT, False)
        if user_opted_out in ['True', 'true', '1']:
            return None
        return func(*args, **kwargs)

    return _wrapper


class TelemetrySession:
    start_time = None
    end_time = None
    correlation_id = str(uuid.uuid4())
    exceptions = []
    server_version = None
    server_edition = None
    connection_type = None

    def add_exception(self, fault_type, description=None):
        details = {
            'Reserved.DataModel.EntityType': 'Fault',
            'Reserved.DataModel.Fault.Description': description or fault_type,
            'Reserved.DataModel.Correlation.1': '{},UserTask,'.format(self.correlation_id),
        }
        fault_name = '{}/{}'.format(PRODUCT_NAME, fault_type.lower())

        self.exceptions.append((fault_name, details))

    @decorators.suppress_all_exceptions(raise_in_diagnostics=True, fallback_return=None)
    def generate_payload(self):
        events = []
        base = self._get_base_properties()

        events.append({'name': PRODUCT_NAME, 'properties': base})
        for name, props in self.exceptions:
            props.update(base)
            props.update({'Reserved.DataModel.CorrelationId': str(uuid.uuid4()),
                          'Reserved.EventId': str(uuid.uuid4())})
            events.append({'name': name, 'properties': props})

        payload = json.dumps(events)
        return _remove_symbols(payload)

    def _get_base_properties(self):

        # Generic data model used by SQL Telemetry.
        return {
            'Reserved.ChannelUsed': 'aivortex',
            'Reserved.SequenceNumber': 1,
            'Reserved.EventId': str(uuid.uuid4()),
            'Reserved.SessionId': str(uuid.uuid4()),
            'Reserved.TimeSinceSessionStart': 0,

            'Reserved.DataModel.Source': 'DataModelAPI',
            'Reserved.DataModel.EntitySchemaVersion': 4,
            'Reserved.DataModel.Severity': 0,
            'Reserved.DataModel.CorrelationId': self.correlation_id,

            'Context.Default.SQLTools.ExeName': PRODUCT_NAME,
            'Context.Default.SQLTools.ExeVersion': _get_mssql_cli_version(),
            'Context.Default.SQLTools.OS.Type': platform.system().lower(),
            'Context.Default.SQLTools.OS.Version': platform.release().lower(),
            'Context.Default.SQLTools.IsDocker': bool(os.environ.get(MSSQL_CLI_IN_DOCKER, False)),
            'Context.Default.SQLTools.User.Id': _get_user_id(),
            'Context.Default.SQLTools.User.IsMicrosoftInternal': 'False',
            'Context.Default.SQLTools.User.IsOptedIn': 'True',
            'Context.Default.SQLTools.ShellType': _get_shell_type(),
            'Context.Default.SQLTools.EnvironmentVariables': _get_env_string(),
            'Context.Default.SQLTools.Locale': '{},{}'.format(locale.getdefaultlocale()[0],
                                                              locale.getdefaultlocale()[1]),
            'Context.Default.SQLTools.StartTime': str(self.start_time),
            'Context.Default.SQLTools.EndTime': str(self.end_time),
            'Context.Default.SQLTools.SessionDuration': str((self.end_time - self.start_time)
                                                            .total_seconds()),
            'Context.Default.SQLTools.PythonVersion': platform.python_version(),
            'Context.Default.SQLTools.ServerVersion': self.server_version,
            'Context.Default.SQLTools.ServerEdition': self.server_edition,
            'Context.Default.SQLTools.ConnectionType': self.connection_type,
        }


_session = TelemetrySession()


# public api

@decorators.suppress_all_exceptions(raise_in_diagnostics=True)
def start():
    _session.start_time = datetime.now()


@decorators.suppress_all_exceptions(raise_in_diagnostics=True)
def conclude(service_endpoint_uri='https://vortex.data.microsoft.com/collect/v1',
             separate_process=True):
    _session.end_time = datetime.now()

    payload = _session.generate_payload()
    output_payload_to_file(payload)
    return upload_payload(payload, service_endpoint_uri, separate_process)


@_user_agrees_to_telemetry
@decorators.suppress_all_exceptions(raise_in_diagnostics=True)
def upload_payload(payload, service_endpoint_uri, separate_process):
    payload_uploaded = None
    if payload:
        if not separate_process:
            telemetry_core.upload(payload, service_endpoint_uri)
        else:
            subprocess.Popen([sys.executable, os.path.realpath(telemetry_core.__file__),
                              payload, service_endpoint_uri])
        payload_uploaded = payload
    return payload_uploaded


@_user_agrees_to_telemetry
@decorators.suppress_all_exceptions(raise_in_diagnostics=True)
def output_payload_to_file(payload):
    if payload:
        config_dir = os.path.dirname(config.config_location())
        telemetry_file_path = os.path.join(config_dir, MSSQL_CLI_TELEMETRY_FILE)

        # Telemetry log file will only contain data points from the most recent session.
        with open(telemetry_file_path, "w+") as telemetry_file:
            json.dump(json.loads(payload), telemetry_file, indent=2)


@decorators.suppress_all_exceptions(raise_in_diagnostics=True)
def set_server_information(connection):

    _session.server_edition = connection.server_edition
    _session.server_version = connection.server_version
    _session.connection_type = 'Azure' if connection.is_cloud else 'Standalone'


# internal utility functions


@decorators.suppress_all_exceptions(fallback_return=None)
def _get_mssql_cli_version():
    return mssql_cli_version


@decorators.suppress_all_exceptions(fallback_return='')
def _get_user_id():
    config_dir = config.config_location()
    full_path = os.path.join(config_dir, MSSQL_CLI_TELEMETRY_ID_FILE)
    if _user_id_file_is_old(full_path) or not os.path.exists(full_path):
        with open(full_path, 'w') as file:
            user_id = _generate_user_id()
            file.write(user_id)
            return user_id
    else:
        with open(full_path, 'r') as file:
            user_id = file.read()
            return user_id


def _user_id_file_is_old(id_file_path):
    if os.path.exists(id_file_path):
        last_24_hours = datetime.now() - timedelta(hours=24)
        id_file_modified_time = datetime.fromtimestamp(os.path.getmtime(id_file_path))

        return id_file_modified_time < last_24_hours
    return False


@decorators.suppress_all_exceptions(fallback_return='')
@decorators.hash256_result
def _generate_user_id():
    random_id = binascii.hexlify(os.urandom(32)).decode() \
        if sys.version_info >= (3, 0) else binascii.hexlify(os.urandom(32))

    return random_id


def _get_env_string():
    return _remove_cmd_chars(_remove_symbols(str([v for v in os.environ
                                                  if v.startswith('MSSQL_CLI_')])))


def _get_shell_type():
    if 'ZSH_VERSION' in os.environ:
        return 'zsh'
    if 'BASH_VERSION' in os.environ:
        return 'bash'
    if 'KSH_VERSION' in os.environ or 'FCEDIT' in os.environ:
        return 'ksh'
    if 'WINDIR' in os.environ:
        return 'cmd'
    return _remove_cmd_chars(_remove_symbols(os.environ.get('SHELL')))


@decorators.suppress_all_exceptions(fallback_return='')
@decorators.hash256_result
def _get_error_hash():
    return str(sys.exc_info()[1])


@decorators.suppress_all_exceptions(fallback_return='')
def _get_stack_trace():
    def _get_root_path():
        dir_path = os.path.dirname(os.path.realpath(__file__))
        head, tail = os.path.split(dir_path)
        while tail and tail != 'mssql-cli':
            head, tail = os.path.split(head)
        return head

    def _remove_root_paths(s):
        site_package_regex = re.compile('.*\\\\site-packages\\\\')

        root = _get_root_path()
        frames = [p.replace(root, '') for p in s]
        return str([site_package_regex.sub('site-packages\\\\', f) for f in frames])

    _, _, ex_traceback = sys.exc_info()
    trace = traceback.format_tb(ex_traceback)
    return _remove_cmd_chars(_remove_symbols(_remove_root_paths(trace)))


def _remove_cmd_chars(s):
    if isinstance(s, str):
        return s.replace("'", '_').replace('"', '_').replace('\r\n', ' ').replace('\n', ' ')
    return s


def _remove_symbols(s):
    if isinstance(s, str):
        for c in '$%^&|':
            s = s.replace(c, '_')
    return s
