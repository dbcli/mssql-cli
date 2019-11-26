from __future__ import print_function

import os
import sys
import tarfile
import zipfile
from future.standard_library import install_aliases
import utility

install_aliases()

SQLTOOLSSERVICE_BASE = os.path.join(utility.ROOT_DIR, 'sqltoolsservice/')

# Supported platform key's must match those in mssqlscript's setup.py.
SUPPORTED_PLATFORMS = {
    'manylinux1_x86_64': SQLTOOLSSERVICE_BASE + 'manylinux1/' +
                         'Microsoft.SqlTools.ServiceLayer-rhel-x64-netcoreapp2.2.tar.gz',
    'macosx_10_11_intel': SQLTOOLSSERVICE_BASE + 'macosx_10_11_intel/' +
                          'Microsoft.SqlTools.ServiceLayer-osx-x64-netcoreapp2.2.tar.gz',
    'win_amd64': SQLTOOLSSERVICE_BASE + 'win_amd64/' +
                 'Microsoft.SqlTools.ServiceLayer-win-x64-netcoreapp2.2.zip',
    'win32': SQLTOOLSSERVICE_BASE + 'win32/' +
             'Microsoft.SqlTools.ServiceLayer-win-x86-netcoreapp2.2.zip'
}

TARGET_DIRECTORY = os.path.abspath(os.path.join(os.path.abspath(__file__), '..', 'bin'))


def copy_sqltoolsservice(platform):
    """
        For each supported platform, build a universal wheel.
    """
    # Clean up dangling directories if previous run was interrupted.
    utility.clean_up(directory=TARGET_DIRECTORY)

    if not platform or platform not in SUPPORTED_PLATFORMS:
        print('{} is not supported.'.format(platform))
        print('Please provide a valid platform flag.' +
              '[win32, win_amd64, manylinux1_x86_64, macosx_10_11_intel]')
        sys.exit(1)

    copy_file_path = SUPPORTED_PLATFORMS[platform]

    print('Sqltoolsservice archive found at {}'.format(copy_file_path))
    if copy_file_path.endswith('tar.gz'):
        compressed_file = tarfile.open(name=copy_file_path, mode='r:gz')
    elif copy_file_path.endswith('.zip'):
        compressed_file = zipfile.ZipFile(copy_file_path)

    if not os.path.exists(TARGET_DIRECTORY):
        os.makedirs(TARGET_DIRECTORY)

    print(u'Bin placing sqltoolsservice for this platform: {}.'.format(platform))
    print(u'Extracting files from {}'.format(copy_file_path))
    compressed_file.extractall(TARGET_DIRECTORY)


def clean_up_sqltoolsservice():
    utility.clean_up(directory=TARGET_DIRECTORY)
