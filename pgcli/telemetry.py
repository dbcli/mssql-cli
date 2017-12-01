import datetime
import json
import locale
import os
import platform
import re
import sys
import traceback
import uuid
from functools import wraps

import pgcli.decorators as decorators
import pgcli.telemetry_upload as telemetry_core
import pgcli.config as config

PRODUCT_NAME = 'mssqlcli'
TELEMETRY_VERSION = '0.0.1'
MSSQL_CLI_PREFIX = 'Context.Default.MSSQLCLI.'
MSSQL_CLI_TELEMETRY_FILE = 'mssqlcli_telemetry.log'
decorators.is_diagnostics_mode = telemetry_core.in_diagnostic_mode


def _user_agrees_to_telemetry(func):
    @wraps(func)
    def _wrapper(*args, **kwargs):
        c = config.get_config()
        if not c['main'].as_bool('collect_telemetry'):
            return
        return func(*args, **kwargs)

    return _wrapper


class TelemetrySession(object):
    start_time = None
    end_time = None
    correlation_id = str(uuid.uuid4())
    exceptions = []
    server_version = None
    server_edition = None
    connection_type = None

    def add_exception(self, exception, fault_type, description=None, message=''):
        details = {
            'Reserved.DataModel.EntityType': 'Fault',
            'Reserved.DataModel.Fault.Description': description or fault_type,
            'Reserved.DataModel.Correlation.1': '{},UserTask,'.format(self.correlation_id),
            'Reserved.DataModel.Fault.TypeString': exception.__class__.__name__
        }
        fault_type = _remove_symbols(fault_type).replace('"', '').replace("'", '').replace(' ', '-')
        fault_name = '{}/{}'.format(PRODUCT_NAME, fault_type.lower())

        self.exceptions.append((fault_name, details))

    @decorators.suppress_all_exceptions(raise_in_diagnostics=True, fallback_return=None)
    def generate_payload(self):
        events = []
        base = self._get_base_properties()
        cli = self._get_mssql_cli_properties()
        cli.update(base)

        events.append({'name': PRODUCT_NAME, 'properties': cli})
        for name, props in self.exceptions:
            props.update(base)
            props.update(cli)
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

            'Context.Default.SQL.Core.ExeName': PRODUCT_NAME,
            'Context.Default.SQL.Core.ExeVersion': _get_mssql_cli_version(),
            'Context.Default.SQL.Core.MacAddressHash': _get_hash_mac_address(),
            'Context.Default.SQL.Core.OS.Type': platform.system().lower(),
            'Context.Default.SQL.Core.OS.Version': platform.version().lower(),
            'Context.Default.SQL.Core.User.IsMicrosoftInternal': 'False',
            'Context.Default.SQL.Core.User.IsOptedIn': 'True',
        }

    def _get_mssql_cli_properties(self):

        # Custom data points used by Mssql-cli.
        result = {}
        self.set_custom_properties(result, 'ShellType', _get_shell_type)
        self.set_custom_properties(result, 'EnvironmentVariables', _get_env_string)
        self.set_custom_properties(result, 'Locale',
                                   lambda: '{},{}'.format(locale.getdefaultlocale()[0],
                                                          locale.getdefaultlocale()[1]))
        self.set_custom_properties(result, 'StartTime', str(self.start_time))
        self.set_custom_properties(result, 'EndTime', str(self.end_time))
        self.set_custom_properties(result, 'SessionDuration', str((self.end_time - self.start_time).total_seconds()))
        self.set_custom_properties(result, 'PythonVersion', platform.python_version())
        self.set_custom_properties(result, 'ServerVersion', _session.server_version)
        self.set_custom_properties(result, 'ServerEdition', _session.server_edition)
        self.set_custom_properties(result, 'ConnectionType', _session.connection_type)

        return result

    @classmethod
    @decorators.suppress_all_exceptions(raise_in_diagnostics=True)
    def set_custom_properties(cls, prop, name, value):
        actual_value = value() if hasattr(value, '__call__') else value
        if actual_value:
            prop[MSSQL_CLI_PREFIX + name] = actual_value


_session = TelemetrySession()


# public api

@decorators.suppress_all_exceptions(raise_in_diagnostics=True)
def start():
    _session.start_time = datetime.datetime.now()


@decorators.suppress_all_exceptions(raise_in_diagnostics=True)
def conclude():
    _session.end_time = datetime.datetime.now()

    payload = _session.generate_payload()
    output_payload_to_file(payload)
    upload_payload(payload)


@_user_agrees_to_telemetry
@decorators.suppress_all_exceptions(raise_in_diagnostics=True)
def upload_payload(payload):
    if payload:
        import subprocess
        subprocess.Popen([sys.executable, os.path.realpath(telemetry_core.__file__), payload])


@decorators.suppress_all_exceptions(raise_in_diagnostics=True)
def output_payload_to_file(payload):
    if payload:
        config_dir = os.path.dirname(config.config_location())
        telemetry_file_path = os.path.join(config_dir, MSSQL_CLI_TELEMETRY_FILE)

        with open(telemetry_file_path, "w+") as telemetry_file:
            json.dump(json.loads(payload), telemetry_file, indent=2)


@decorators.suppress_all_exceptions(raise_in_diagnostics=True)
def set_exception(exception, fault_type, summary=None):
    _session.add_exception(exception, fault_type=fault_type, description=summary)


@decorators.suppress_all_exceptions(raise_in_diagnostics=True)
def set_server_information(connection):

    _session.server_edition = connection.server_edition
    _session.server_version = connection.server_version
    _session.connection_type = 'Azure' if connection.is_cloud else 'Standalone'


# internal utility functions


@decorators.suppress_all_exceptions(fallback_return=None)
def _get_mssql_cli_version():
    from pgcli import __version__ as mssql_cli_version
    return mssql_cli_version


@decorators.suppress_all_exceptions(fallback_return='')
@decorators.hash256_result
def _get_hash_mac_address():
    s = ''
    for index, c in enumerate(hex(uuid.getnode())[2:].upper()):
        s += c
        if index % 2:
            s += '-'

    s = s.strip('-')

    return s


def _get_env_string():
    return _remove_cmd_chars(_remove_symbols(str([v for v in os.environ
                                                  if v.startswith('MSSQLCLI')])))


def _get_shell_type():
    if 'ZSH_VERSION' in os.environ:
        return 'zsh'
    elif 'BASH_VERSION' in os.environ:
        return 'bash'
    elif 'KSH_VERSION' in os.environ or 'FCEDIT' in os.environ:
        return 'ksh'
    elif 'WINDIR' in os.environ:
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
