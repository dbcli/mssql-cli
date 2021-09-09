import ast
import os
import re
import datetime
# pylint: disable=redefined-builtin
from codecs import open
from setuptools import setup, find_packages

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('mssqlcli/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

description = 'CLI for SQL Server Database. With auto-completion and syntax highlighting.'

MSSQLTOOLSSERVICE_VERSION = '1.0.0a21'


def get_timestamped_version(ver):
    """
    Appends .dev<DateTimeString> to version.
    :param version: The version number
    :return: <version>.dev<YearMonthDayHourMinute>. Example 0.0.1.dev1711030310
    """
    return ver + '.dev' + datetime.datetime.now().strftime("%y%m%d%H%M")


install_requirements = [
    'click >= 4.1,<7.1',
    'Pygments >= 2.0',  # Pygments has to be Capitalcased.
    'prompt_toolkit>=2.0.6,<4.0.0;python_version>"2.7"',
    'prompt_toolkit>=2.0.6,<3.0.0;python_version<="2.7"',
    'sqlparse >=0.3.0,<0.5',
    'configobj >= 5.0.6',
    'humanize >= 0.5.1',
    'cli_helpers[styles] >= 2.0.0;python_version>"2.7"',
    'cli_helpers < 1.2.0;python_version<="2.7"',
    'applicationinsights>=0.11.1',
    'future>=0.16.0',
    'wheel>=0.29.0',
    'enum34>=1.1.6;python_version<"3.4"'
]

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='mssql-cli',
    author='Microsoft Corporation',
    author_email='sqlcli@microsoft.com',
    version=version if os.environ.get('MSSQL_CLI_OFFICIAL_BUILD', '').lower() == 'true'
                    else get_timestamped_version(version),
    license='BSD-3',
    url='https://github.com/dbcli/mssql-cli',
    packages=find_packages(),
    package_data={'mssqlcli': ['mssqlclirc',
                               'packages/mssqlliterals/sqlliterals.json']},
    description=description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=install_requirements,
    include_package_data=True,
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
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: SQL',
        'Topic :: Database',
        'Topic :: Database :: Front-Ends',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
