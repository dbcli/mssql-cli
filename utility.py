from __future__ import print_function
from subprocess import check_call, CalledProcessError
import os
import shutil
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

MSSQLCLI_DIST_DIRECTORY = os.path.abspath(
    os.path.join(os.path.abspath(__file__), '..', 'dist'))


def exec_command(command, directory, continue_on_error=True):
    """
        Execute command.
    """
    try:
        check_call(command.split(), cwd=directory)
    except CalledProcessError as err:
        # Continue execution in scenarios where we may be bulk command execution.
        print(err, file=sys.stderr)
        if not continue_on_error:
            sys.exit(1)
        else:
            pass


def cleaun_up_egg_info_sub_directories(directory):
    for f in os.listdir(directory):
        if f.endswith(".egg-info"):
            clean_up(os.path.join(directory, f))


def clean_up(directory):
    """
        Delete directory.
    """
    try:
        shutil.rmtree(directory)
    except Exception:
        # Ignored, directory may not exist which is fine.
        pass
