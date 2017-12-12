from __future__ import print_function
import os
import sys
import utility
import mssqlcli.mssqltoolsservice.externals as mssqltoolsservice


def print_heading(heading, f=None):
    print('{0}\n{1}\n{0}'.format('=' * len(heading), heading), file=f)


def clean_and_copy_sqltoolsservice(platform):
    """
        Cleans the SqlToolsService directory and copies over the SqlToolsService binaries for the given platform.
        :param platform: string
    """
    mssqltoolsservice.clean_up_sqltoolsservice()
    mssqltoolsservice.copy_sqltoolsservice(platform)


def code_analysis():
    utility.exec_command(
        'flake8 mssqlcli setup.py dev_setup.py build.py utility.py dos2unix.py',
        utility.ROOT_DIR)


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
    utility.exec_command(
        'pip install -r requirements-dev.txt',
        utility.ROOT_DIR)

    # convert windows line endings to unix for mssql-cli bash script
    utility.exec_command(
        'python dos2unix.py mssql-cli mssql-cli',
        utility.ROOT_DIR)

    # run flake8
    code_analysis()

    if utility.get_current_platform().startswith('win'):
        platforms_to_build = ['win32', 'win_amd64']
    else:
        platforms_to_build = [utility.get_current_platform()]

    for platform in platforms_to_build:
        # For the current platform, populate the appropriate binaries and
        # generate the wheel.
        clean_and_copy_sqltoolsservice(platform)
        utility.clean_up(utility.MSSQLCLI_BUILD_DIRECTORY)

        print_heading('Building mssql-cli pip package')
        utility.exec_command('python --version', utility.ROOT_DIR)
        utility.exec_command('python setup.py check -r -s bdist_wheel --plat-name {}'.format(platform),
                             utility.ROOT_DIR,
                             continue_on_error=False)

    # Copy back the SqlToolsService binaries for this platform.
    clean_and_copy_sqltoolsservice(utility.get_current_platform())


def validate_package():
    """
        Install mssql-cli package locally.
    """
    root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))
    # Local install of mssql-scripter.
    mssqlcli_wheel_dir = os.listdir(utility.MSSQLCLI_DIST_DIRECTORY)
    # To ensure we have a clean install, we disable the cache as to prevent
    # cache overshadowing actual changes made.
    current_platform = utility.get_current_platform()

    mssqlcli_wheel_name = [
        pkge for pkge in mssqlcli_wheel_dir if current_platform in pkge]
    utility.exec_command(
        'pip install --no-cache-dir --no-index ./dist/{}'.format(
            mssqlcli_wheel_name[0]),
        root_dir, continue_on_error=False
    )


def unit_test():
    """
    Run all unit tests.
    """
    utility.exec_command(
        'pytest --cov mssqlcli tests/test_mssqlcliclient.py tests/test_main.py tests/test_fuzzy_completion.py '
        'tests/test_rowlimit.py tests/test_sqlcompletion.py tests/test_prioritization.py mssqlcli/jsonrpc/contracts/tests '
        'tests/test_telemetry.py',
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
        'test': test
    }
    actions = sys.argv[1:] or default_actions

    for action in actions:
        if action in targets:
            targets[action]()
        else:
            print('{0} is not a supported action'.format(action[1]))
            print('Supported actions are {}'.format(list(targets.keys())))
