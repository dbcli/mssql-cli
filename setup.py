# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import ast
import os
import platform
import re
import sys
import datetime

from setuptools import setup, find_packages

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('pgcli/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

description = 'CLI for SQL Server Database. With auto-completion and syntax highlighting.'

MSSQLTOOLSSERVICE_VERSION = '1.0.0a21'
MSSQLTOOLSSERVICE_PACKAGE_NAME = 'mssqltoolsservice-{}=={}'
MSSQLTOOLSSERVICE_PACKAGE_SUFFIX = [
    'OSX_10_11_64',
    'Windows_7_64',
    'Windows_7_86',
    'Linux_64'
]


def _get_runtime_id(
        system=platform.system(),
        architecture=platform.architecture()[0]):
    """
        Find supported run time id for current platform.
    """
    run_time_id = None

    if system == 'Windows':
        if architecture == '32bit':
            run_time_id = 'Windows_7_86'
        elif architecture == '64bit':
            run_time_id = 'Windows_7_64'
    elif system == 'Darwin':
        if architecture == '64bit':
            run_time_id = 'OSX_10_11_64'
    elif system == 'Linux':
        if architecture == '64bit':
            run_time_id = 'Linux_64'

    return run_time_id


def get_mssqltoolsservice_package_name(run_time_id=_get_runtime_id()):
    """
        Retrieve sql tools service package name for this platform if supported.
    """
    if run_time_id and run_time_id in MSSQLTOOLSSERVICE_PACKAGE_SUFFIX:
        # set package suffix name for other uses like building wheels outside of setup.py.
        os.environ['MSSQLTOOLSSERVICE_PACKAGE_SUFFIX'] = run_time_id
        return MSSQLTOOLSSERVICE_PACKAGE_NAME.format(
            run_time_id, MSSQLTOOLSSERVICE_VERSION).replace('_', '-').lower()

    raise EnvironmentError('mssqltoolsservice is not supported on this platform.')


def get_timestamped_version(version):
    """
    Appends .dev<DateTimeString> to version.
    :param version: The version number
    :return: <version>.dev<YearMonthDayHourMinute>. Example 0.0.1.dev1711030310
    """
    return version+'.dev'+datetime.datetime.now().strftime("%y%m%d%I%M")

install_requirements = [
    'pgspecial>=1.8.0',
    'click >= 4.1',
    'Pygments >= 2.0',  # Pygments has to be Capitalcased.
    'prompt_toolkit>=1.0.10,<1.1.0',
    'psycopg2 >= 2.5.4',
    'sqlparse >=0.2.2,<0.3.0',
    'configobj >= 5.0.6',
    'humanize >= 0.5.1',
    'cli_helpers >= 0.2.3, < 1.0.0',
    'future>=0.16.0',
    'wheel>=0.29.0'
]

if sys.version_info < (3, 4):
    install_requirements.append('enum34>=1.1.6')

install_requirements.append(get_mssqltoolsservice_package_name())

# Using a environment variable to communicate mssqltoolsservice package name for
# other modules that need that info like dev_setup.py.
os.environ['MSSQLTOOLSSERVICE_PACKAGE_NAME'] = install_requirements[-1]

# setproctitle is used to mask the password when running `ps` in command line.
# But this is not necessary in Windows since the password is never shown in the
# task manager. Also setproctitle is a hard dependency to install in Windows,
# so we'll only install it if we're not in Windows.
if platform.system() != 'Windows' and not platform.system().startswith("CYGWIN"):
    install_requirements.append('setproctitle >= 1.1.9')


setup(
    name='mssql-cli',
    author='Microsoft Corporation',
    author_email='sqlcli@microsoft.com',
    version=get_timestamped_version(version),
    license='MIT',
    url='https://github.com/Microsoft/mssql-cli',
    packages=find_packages(),
    package_data={'pgcli': ['pgclirc',
                            'packages/pgliterals/sqlliterals.json']},
    description=description,
    long_description=open('README.rst').read(),
    install_requires=install_requirements,
    scripts=[
        'mssql-cli.bat',
        'mssql-cli'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: SQL',
        'Topic :: Database',
        'Topic :: Database :: Front-Ends',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
