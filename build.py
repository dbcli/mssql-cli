from __future__ import print_function
from shutil import copyfile

import os
import sys
import uuid
import platform
import polib
import utility
import mssqlcli.mssqltoolsservice.externals as mssqltoolsservice


# Environment variables below allow the build process to use a python interpreter and pip version
# different from the user's PATH. When building our linux packages on various distros, we want to
# be build machine agnostic, so we redirect python calls to the python we bundle in. Usage of
# these variables can be seen in our build_scripts folder.
PIP = os.getenv('CUSTOM_PIP', 'pip')
PYTHON = os.getenv('CUSTOM_PYTHON', 'python')


def print_heading(heading, f=None):
    print('{0}\n{1}\n{0}'.format('=' * len(heading), heading), file=f)


def clean_and_copy_sqltoolsservice(plat):
    """
        Cleans the SqlToolsService directory and copies over the SqlToolsService binaries for the
        given platform.
        :param platform: string
    """
    mssqltoolsservice.clean_up_sqltoolsservice()
    mssqltoolsservice.copy_sqltoolsservice(plat)


def code_analysis():
    utility.exec_command(
        '%s -m flake8 mssqlcli setup.py dev_setup.py build.py utility.py dos2unix.py' % PYTHON,
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
        '{0} install -r requirements-dev.txt'.format(PIP),
        utility.ROOT_DIR)

    # convert windows line endings to unix for mssql-cli bash script
    utility.exec_command(
        '{0} dos2unix.py mssql-cli mssql-cli'.format(PYTHON),
        utility.ROOT_DIR)

    # run flake8
    code_analysis()

    if utility.get_current_platform().startswith('win'):
        platforms_to_build = ['win32', 'win_amd64']
    else:
        platforms_to_build = [utility.get_current_platform()]

    for plat in platforms_to_build:
        # For the current platform, populate the appropriate binaries and
        # generate the wheel.
        clean_and_copy_sqltoolsservice(plat)
        utility.clean_up(utility.MSSQLCLI_BUILD_DIRECTORY)

        print_heading('Building mssql-cli pip package')
        utility.exec_command('%s --version' % PYTHON, utility.ROOT_DIR)
        utility.exec_command('%s setup.py bdist_wheel --plat-name %s' % (PYTHON, plat),
                             utility.ROOT_DIR,
                             continue_on_error=False)

        try:
            # checks if long description will render correctly--does not work on some systems
            utility.exec_command('twine check {}'
                                .format(os.path.join(utility.MSSQLCLI_DIST_DIRECTORY, '*')),
                                utility.ROOT_DIR, continue_on_error=False)
        except IOError:
            print("Unable to run 'twine check'.")

    # Copy back the SqlToolsService binaries for this platform.
    clean_and_copy_sqltoolsservice(utility.get_current_platform())
    copy_and_rename_wheels()


def copy_and_rename_wheels():
    # Create a additional copy of each build artifact with a ever green name with 'dev-latest' as
    # it's version.
    for pkg_name in os.listdir(utility.MSSQLCLI_DIST_DIRECTORY):
        file_name, file_extension = os.path.splitext(pkg_name)

        if file_extension == '.gz':
            file_extension = '.tar.gz'
            # rename sdist to make underscore consistent with wheel
            file_name = file_name.replace('mssql-cli', 'mssql_cli').replace('.tar', '')
            os.rename(os.path.join(utility.MSSQLCLI_DIST_DIRECTORY, pkg_name),
                      os.path.join(utility.MSSQLCLI_DIST_DIRECTORY, file_name + file_extension))
            pkg_name = file_name + file_extension

            end_index_to_replace = len(file_name)

        first_dash = file_name.find('-')

        if file_extension == '.whl':
            end_index_to_replace = file_name.find('-', first_dash + 1, len(file_name))

        pkg_daily_name = file_name.replace(file_name[first_dash + 1:end_index_to_replace],
                                           'dev-latest')

        original_path = os.path.join(utility.MSSQLCLI_DIST_DIRECTORY, pkg_name)
        updated_path = os.path.join(utility.MSSQLCLI_DIST_DIRECTORY,
                                    pkg_daily_name + file_extension)
        copyfile(original_path, updated_path)


def validate_package():
    """
        Install mssql-cli package locally.
    """
    root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))
    # Local install of mssql-cli.
    mssqlcli_wheel_dir = os.listdir(utility.MSSQLCLI_DIST_DIRECTORY)
    # To ensure we have a clean install, we disable the cache as to prevent
    # cache overshadowing actual changes made.
    current_platform = utility.get_current_platform()

    mssqlcli_wheel_name = [pkge for pkge in mssqlcli_wheel_dir
                           if current_platform in pkge and 'dev-latest' not in pkge]
    utility.exec_command(
        '{0} install --no-cache-dir --no-index ./dist/{1}'.format(
            PIP,
            mssqlcli_wheel_name[0]),
        root_dir, continue_on_error=False
    )


def unit_test():
    """
    Run all unit tests.
    """
    runid = str(uuid.uuid1())
    python_version = platform.python_version()
    utility.exec_command(('pytest -l --cov mssqlcli --doctest-modules '
                          '--junitxml=junit/test-{}-results.xml --cov-report=xml '
                          '--cov-report=html --cov-append -o junit_suite_name=pytest-{} '
                          '-m "not unstable" {}').format(runid, python_version,
                                                         get_active_test_filepaths()),
                         utility.ROOT_DIR, continue_on_error=False)


def unstable_unit_test():
    """
    Run all unstable unit tests.
    """
    runid = str(uuid.uuid1())
    utility.exec_command('pytest --doctest-modules --junitxml=junit/test-unstable-{}-results.xml '
                         '-s -v -m unstable {}'.format(runid, get_active_test_filepaths()),
                         utility.ROOT_DIR, continue_on_error=False)


def get_active_test_filepaths():
    return (
        'tests/test_mssqlcliclient.py '
        'tests/test_completion_refresher.py '
        'tests/test_config.py '
        'tests/test_naive_completion.py '
        'tests/test_main.py '
        'tests/test_multiline.py '
        'tests/test_fuzzy_completion.py '
        'tests/test_rowlimit.py '
        'tests/test_sqlcompletion.py '
        'tests/test_prioritization.py '
        'tests/jsonrpc '
        'tests/test_telemetry.py '
        'tests/test_localization.py '
        'tests/test_globalization.py '
        'tests/test_interactive_mode.py '
        'tests/test_noninteractive_mode.py '
        'tests/test_special.py'
    )


def integration_test():
    """
    Run full integration test via tox which includes build, unit tests, code coverage,
    and packaging.
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


def validate_actions(user_actions, valid_targets):
    for user_action in user_actions:
        if user_action.lower() not in valid_targets.keys():
            print('{0} is not a supported action'.format(user_action))
            print('Supported actions are {}'.format(list(valid_targets.keys())))
            sys.exit(1)


def generate_mo(extraction_target_path, lang_name, trans_mappings, domain, localedir=None):
    """
    Extracts strings from 'extraction_target_path', and creates pot, po, mo file with
    'trans_mappings' information.
    'extraction_target_path' can be file or directory.
    """
    extraction_target_dir = extraction_target_path\
        if os.path.isdir(extraction_target_path) else os.path.dirname(extraction_target_path)
    localedir = localedir if localedir is not None \
                          else os.path.join(extraction_target_dir, 'locale')
    mo_dir = os.path.join(localedir, lang_name, 'LC_MESSAGES')
    create_dir([extraction_target_dir, 'locale', lang_name, 'LC_MESSAGES'])

    pot_file = '{0}.pot'.format(os.path.join(localedir, domain))
    po_file = '{0}.po'.format(os.path.join(mo_dir, domain))
    mo_file = '{0}.mo'.format(os.path.join(mo_dir, domain))

    extract_command = "pybabel extract {0} -o {1}".format(extraction_target_path, pot_file)
    utility.exec_command(extract_command, extraction_target_dir)

    po = polib.pofile(pot_file)
    for entry in po:
        if entry.msgid in trans_mappings:
            entry.msgstr = trans_mappings[entry.msgid]
    po.save(po_file)
    po.save_as_mofile(mo_file)
    return domain, localedir


def create_dir(path):
    curr_path = None
    for p in path:
        if curr_path is None:
            curr_path = os.path.abspath(p)
        else:
            curr_path = os.path.join(curr_path, p)
        if not os.path.exists(curr_path):
            os.mkdir(curr_path)


if __name__ == '__main__':
    default_actions = ['build', 'unit_test']

    targets = {
        'build': build,
        'validate_package': validate_package,
        'unit_test': unit_test,
        'unstable_unit_test': unstable_unit_test,
        'integration_test': integration_test,
        'test': test
    }
    actions = sys.argv[1:] or default_actions

    validate_actions(actions, targets)

    for action in actions:
        targets[action.lower()]()
