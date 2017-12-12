from __future__ import print_function
from azure.storage.blob import BlockBlobService
import os
import sys
import utility

AZURE_STORAGE_CONNECTION_STRING = os.environ.get(
    'AZURE_STORAGE_CONNECTION_STRING')
BLOB_MSSQL_CLI_DAILY_CONTAINER_NAME = 'daily/mssql-cli'


def download_official_wheels():
    """
        Download the official wheels for each platform
    """
    assert AZURE_STORAGE_CONNECTION_STRING, 'Set AZURE_STORAGE_CONNECTION_STRING environment variable'
    from mssqlcli import __version__ as latest_version

    # Clear previous downloads
    utility.clean_up(utility.MSSQLCLI_DIST_DIRECTORY)
    os.mkdir(utility.MSSQLCLI_DIST_DIRECTORY)

    print('Downloading official wheels with version: {}'.format(latest_version))
    blob_names = [
        'mssql_cli-{}-py2.py3-none-macosx_10_11_intel.whl'.format(latest_version),
        'mssql_cli-{}-py2.py3-none-manylinux1_x86_64.whl'.format(latest_version),
        'mssql_cli-{}-py2.py3-none-win_amd64.whl'.format(latest_version),
        'mssql_cli-{}-py2.py3-none-win32.whl'.format(latest_version)
    ]

    blob_service = BlockBlobService(connection_string=AZURE_STORAGE_CONNECTION_STRING)
    for blob in blob_names:
        print('Downloading wheel:{}'.format(blob))

        if not blob_service.exists(BLOB_MSSQL_CLI_DAILY_CONTAINER_NAME, blob):
            print('Error: blob: {} does not exist in container: {}'.format(blob, BLOB_MSSQL_CLI_DAILY_CONTAINER_NAME))
            sys.exit(1)

        blob_service.get_blob_to_path(BLOB_MSSQL_CLI_DAILY_CONTAINER_NAME, blob, '{0}\{1}'.format(
                                                                                        utility.MSSQLCLI_DIST_DIRECTORY,
                                                                                        blob))


def publish_official():
    """
    Publish mssql-cli package to PyPi.
    """
    mssqlcli_wheel_dir = os.listdir(utility.MSSQLCLI_DIST_DIRECTORY)
    # Run twine action for mssql-cli.
    # Only authorized users with credentials will be able to upload this package.
    # Credentials will be stored in a .pypirc file.
    for wheel in mssqlcli_wheel_dir:
        utility.exec_command(
            'twine upload {}'.format(wheel),
            utility.MSSQLCLI_DIST_DIRECTORY)


if __name__ == '__main__':
    default_actions = ['download_official_wheels']

    targets = {
        'publish_official': publish_official,
        'download_official_wheels': download_official_wheels
    }
    actions = sys.argv[1:] or default_actions

    for action in actions:
        if action in targets:
            targets[action]()
        else:
            print('{0} is not a supported action'.format(action[1]))
            print('Supported actions are {}'.format(list(targets.keys())))