#!/usr/bin/env python
from __future__ import print_function
import utility

print('Running dev setup...')
print('Root directory \'{}\'\n'.format(utility.ROOT_DIR))

# install general requirements.
utility.exec_command('pip install --no-cache-dir -r requirements-dev.txt', utility.ROOT_DIR)

# install mssqltoolsservice if this platform supports it.
utility.copy_current_platform_mssqltoolsservice()

print('Finished dev setup.')
