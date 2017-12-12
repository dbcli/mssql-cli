from __future__ import print_function
from azure.storage.blob import BlockBlobService, ContentSettings
import os
import sys
import utility

AZURE_STORAGE_CONNECTION_STRING = os.environ.get(
    'AZURE_STORAGE_CONNECTION_STRING')
BLOB_MSSQL_CLI_DAILY_CONTAINER_NAME = 'daily/mssql-cli'
BLOB_CONTAINER_NAME = 'daily'
UPLOADED_PACKAGE_LINKS = []


def print_heading(heading, f=None):
    print('{0}\n{1}\n{0}'.format('=' * len(heading), heading), file=f)


def _upload_index_file(service, blob_name, title, links):
    print('Uploading index file {}'.format(blob_name))
    service.create_blob_from_text(
        container_name=BLOB_CONTAINER_NAME,
        blob_name=blob_name,
        text="<html><head><title>{0}</title></head><body><h1>{0}</h1>{1}</body></html>"
        .format(title, '\n'.join(
                ['<a href="{0}">{0}</a><br/>'.format(link) for link in links])),
        content_settings=ContentSettings(
            content_type='text/html',
            content_disposition=None,
            content_encoding=None,
            content_language=None,
            content_md5=None,
            cache_control=None
        )
    )


def _gen_pkg_index_html(service, pkg_name):
    links = []
    index_file_name = pkg_name + '/'
    for blob in list(service.list_blobs(
            BLOB_CONTAINER_NAME, prefix=index_file_name)):
        if blob.name == index_file_name:
            # Exclude the index file from being added to the list
            continue
        links.append(blob.name.replace(index_file_name, ''))
    _upload_index_file(
        service,
        index_file_name,
        'Links for {}'.format(pkg_name),
        links)
    UPLOADED_PACKAGE_LINKS.append(index_file_name)


def _upload_package(service, file_path, pkg_name):
    print('Uploading {}'.format(file_path))
    file_name = os.path.basename(file_path)
    blob_name = '{}/{}'.format(pkg_name, file_name)
    service.create_blob_from_path(
        container_name=BLOB_CONTAINER_NAME,
        blob_name=blob_name,
        file_path=file_path
    )


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


def publish_daily():
    """
    Publish mssql-cli package to daily storage account.
    """
    print('Publishing to daily container within storage account.')
    assert AZURE_STORAGE_CONNECTION_STRING, 'Set AZURE_STORAGE_CONNECTION_STRING environment variable'

    blob_service = BlockBlobService(
        connection_string=AZURE_STORAGE_CONNECTION_STRING)

    print_heading('Uploading packages to blob storage ')
    for pkg in os.listdir(utility.MSSQLCLI_DIST_DIRECTORY):
        pkg_path = os.path.join(utility.MSSQLCLI_DIST_DIRECTORY, pkg)
        print('Uploading package {}'.format(pkg_path))
        _upload_package(blob_service, pkg_path, 'mssql-cli')

    _gen_pkg_index_html(blob_service, 'mssql-cli')
    _upload_index_file(
        blob_service,
        'index.html',
        'Simple Index',
        UPLOADED_PACKAGE_LINKS)


if __name__ == '__main__':
    default_actions = ['download_official_wheels']

    targets = {
        'publish_daily': publish_daily,
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
