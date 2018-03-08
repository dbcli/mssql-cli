#!/usr/bin/env python
from __future__ import print_function
import os
import utility

PIP = os.getenv('PIP_PATH', 'pip')

print('Running dev setup...')
print('Root directory \'{}\'\n'.format(utility.ROOT_DIR))

# install general requirements.
utility.exec_command('{0} install -r requirements-dev.txt'.format(PIP), utility.ROOT_DIR)

# install mssqltoolsservice if this platform supports it.
utility.copy_current_platform_mssqltoolsservice()

print('Finished dev setup.')
