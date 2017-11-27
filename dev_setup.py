#!/usr/bin/env python
from __future__ import print_function
import utility
import platform

print('Running dev setup...')
print('Root directory \'{}\'\n'.format(utility.ROOT_DIR))

# install general requirements.
utility.exec_command('pip install -r requirements-dev.txt', utility.ROOT_DIR)

# setproctitle is used to mask the password when running `ps` in command line.
# But this is not necessary in Windows since the password is never shown in the
# task manager. Also setproctitle is a hard dependency to install in Windows,
# so we'll only install it if we're not in Windows.
if platform.system() != 'Windows' and not platform.system().startswith("CYGWIN"):
    utility.exec_command('pip install setproctitle >= 1.1.9', utility.ROOT_DIR)

# install mssqltoolsservice if this platform supports it.
utility.copy_current_platform_mssqltoolsservice()

print('Finished dev setup.')
