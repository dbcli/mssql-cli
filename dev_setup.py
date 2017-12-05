#!/usr/bin/env python
from __future__ import print_function
import utility

print('Running dev setup...')
print('Root directory \'{}\'\n'.format(utility.ROOT_DIR))

# install general requirements.
utility.exec_command('pip install -r requirements-dev.txt', utility.ROOT_DIR)

platform = utility.get_current_platform()
if platform != 'win32' and platform != 'win_amd64':
    utility.exec_command('pip install setproctitle>=1.1.9', utility.ROOT_DIR)

# install mssqltoolsservice if this platform supports it.
utility.copy_current_platform_mssqltoolsservice()

print('Finished dev setup.')
