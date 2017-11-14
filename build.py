from __future__ import print_function
from azure.storage.blob import BlockBlobService, ContentSettings
import os
import sys
import utility

AZURE_STORAGE_CONNECTION_STRING = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
BLOB_CONTAINER_NAME = 'daily'
UPLOADED_PACKAGE_LINKS = []


def print_heading(heading, f=None):
    print('{0}\n{1}\n{0}'.format('=' * len(heading), heading), file=f)


def build():
    """
        Builds mssql-cli package.
    """
    print_heading('Cleanup')

    # clean
    utility.clean_up(utility.MSSQLCLI_DIST_DIRECTORY)
    utility.clean_up_egg_info_sub_directories(utility.ROOT_DIR)

    print_heading('Running setup')

    # install general requirements.
    utility.exec_command('pip install -r requirements-dev.txt', utility.ROOT_DIR)

    # convert windows line endings to unix for mssql-cli bash script
    utility.exec_command('python dos2unix.py mssql-cli mssql-cli', utility.ROOT_DIR)

    print_heading('Building mssql-cli pip package')
    utility.exec_command('python --version', utility.ROOT_DIR)
    utility.exec_command('python setup.py check -r -s sdist', utility.ROOT_DIR, continue_on_error=False)


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
    index_file_name = pkg_name+'/'
    for blob in list(service.list_blobs(BLOB_CONTAINER_NAME, prefix=index_file_name)):
        if blob.name == index_file_name:
            # Exclude the index file from being added to the list
            continue
        links.append(blob.name.replace(index_file_name, ''))
    _upload_index_file(service, index_file_name, 'Links for {}'.format(pkg_name), links)
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
    _gen_pkg_index_html(service, pkg_name)


def validate_package():
    """
        Install mssql-cli package locally.
    """
    root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))
    # Local install of mssql-scripter.
    mssqlcli_sdist_name = os.listdir(utility.MSSQLCLI_DIST_DIRECTORY)[0]
    # To ensure we have a clean install, we disable the cache as to prevent cache overshadowing actual changes made.
    utility.exec_command(
        'pip install --no-cache-dir --no-index ./dist/{}'.format(mssqlcli_sdist_name),
        root_dir, continue_on_error=False
    )


def publish_daily():
    """
    Publish mssql-cli package to daily storage account.
    """
    print('Publishing to daily container within storage account.')
    assert AZURE_STORAGE_CONNECTION_STRING, 'Set AZURE_STORAGE_CONNECTION_STRING environment variable'

    blob_service = BlockBlobService(connection_string=AZURE_STORAGE_CONNECTION_STRING)

    print_heading('Uploading packages to blob storage ')
    for pkg in os.listdir(utility.MSSQLCLI_DIST_DIRECTORY):
        pkg_path = os.path.join(utility.MSSQLCLI_DIST_DIRECTORY, pkg)
        print('Uploading package {}'.format(pkg_path))
        _upload_package(blob_service, pkg_path, 'mssql-cli')
    # Upload the final index file
    _upload_index_file(blob_service, 'index.html', 'Simple Index', UPLOADED_PACKAGE_LINKS)


def publish_official():
    """
    Publish mssql-cli package to PyPi.
    """
    mssqlcli_sdist_name = os.listdir(utility.MSSQLCLI_DIST_DIRECTORY)[0]
    # Run twine action for mssqlscripter.
    # Only authorized users with credentials will be able to upload this package.
    # Credentials will be stored in a .pypirc file.
    utility.exec_command(
        'twine upload {} pypi'.format(mssqlcli_sdist_name),
        utility.MSSQLCLI_DIST_DIRECTORY)


def unit_test():
    """
    Run all unit tests.
    """
    utility.exec_command(
        'pytest --cov pgcli tests/test_mssqlcliclient.py tests/test_main.py tests/test_fuzzy_completion.py '
        'tests/test_rowlimit.py tests/test_sqlcompletion.py tests/test_prioritization.py pgcli/jsonrpc/contracts/tests',
        utility.ROOT_DIR,
        continue_on_error=False)


def integration_test():
    """
    Run full integration test via tox which includes build, unit tests, code coverage, and packaging.
    """
    utility.exec_command(
        'tox',
        utility.ROOT_DIR,
        continue_on_error=False)


def test():
    """
    Run unit test and integration test.
    """
    unit_test()
    integration_test()


if __name__ == '__main__':
    default_actions = ['build', 'unit_test']

    targets = {
        'build': build,
        'validate_package': validate_package,
        'unit_test': unit_test,
        'integration_test': integration_test,
        'test': test,
        'publish_daily': publish_daily,
        'publish_official': publish_official
    }
    actions = sys.argv[1:] or default_actions

    for action in actions:
        if action in targets:
            targets[action]()
        else:
            print('{0} is not a supported action'.format(action[1]))
            print('Supported actions are {}'.format(list(targets.keys())))
