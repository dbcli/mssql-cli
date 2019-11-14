from __future__ import print_function
from subprocess import check_call, CalledProcessError
import os
import platform
import shutil
import sys
import string
import random

ROOT_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

MSSQLCLI_DIST_DIRECTORY = os.path.abspath(
    os.path.join(os.path.abspath(__file__), '..', 'dist'))

MSSQLCLI_BUILD_DIRECTORY = os.path.abspath(
    os.path.join(os.path.abspath(__file__), '..', 'build'))


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


def clean_up_egg_info_sub_directories(directory):
    for f in os.listdir(directory):
        if f.endswith(".egg-info"):
            clean_up(os.path.join(directory, f))


def clean_up(directory):
    """
        Delete directory.
    """
    try:
        shutil.rmtree(directory)
    except OSError:
        # Ignored, directory may not exist which is fine.
        pass


def get_current_platform():
    """
        Get current platform name.
    """
    system = platform.system()
    arch = platform.architecture()[0]

    run_time_id = None
    if system == 'Windows':
        if arch == '32bit':
            run_time_id = 'win32'
        elif arch == '64bit':
            run_time_id = 'win_amd64'
    elif system == 'Darwin':
        run_time_id = 'macosx_10_11_intel'
    elif system == 'Linux':
        run_time_id = 'manylinux1_x86_64'

    return run_time_id


def copy_current_platform_mssqltoolsservice():
    """
    Copy the necessary mssqltoolsservice binaries for the current platform if supported.
    """
    # pylint: disable=import-outside-toplevel
    import mssqlcli.mssqltoolsservice.externals as mssqltoolsservice

    current_platform = get_current_platform()
    if current_platform:
        mssqltoolsservice.copy_sqltoolsservice(current_platform)
    else:
        print("This platform: {} does not support mssqltoolsservice.".format(platform.system()))


def encode(s):
    try:
        return s.encode('utf-8')
    except:     #pylint: disable=bare-except
        pass
    return s


# In Python 3, all strings are sequences of Unicode characters.
# There is a bytes type that holds raw bytes.
# In Python 2, a string may be of type str or of type unicode.
def decode(s):
    try:
        return s.decode('utf-8')
    except:     #pylint: disable=bare-except
        pass
    return s


def random_str(size=12, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))
