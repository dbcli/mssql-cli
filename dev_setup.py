#!/usr/bin/env python
from __future__ import print_function
import sys
import utility

PIP = 'pip3' if sys.version_info[0] == 3 else 'pip'

print('Running dev setup...')
print('Root directory \'{}\'\n'.format(utility.ROOT_DIR))

# install general requirements.
utility.exec_command('{0} install -r requirements-dev.txt'.format(PIP), utility.ROOT_DIR)

# install mssqltoolsservice if this platform supports it.
utility.copy_current_platform_mssqltoolsservice()

print('Finished dev setup.')
