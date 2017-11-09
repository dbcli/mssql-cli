#!/usr/bin/env python
# this must be executed as "python dev_setup.py clean" to prevent invoking the other options from setup.
from __future__ import print_function
import os
# Importing setup.py gives us the environment variable set to discover mssqltoolsservice name.
import setup
import utility

print('Running dev setup...')
print('Root directory \'{}\'\n'.format(utility.ROOT_DIR))

# install general requirements.
utility.exec_command('pip install -r requirements-dev.txt', utility.ROOT_DIR)

# install mssqltoolsservice if this platform supports it.
# Environment variable is set by importing setup.
mssqltoolsservice_package_name = os.environ['MSSQLTOOLSSERVICE_PACKAGE_NAME']
print('Installing {}...'.format(mssqltoolsservice_package_name))
# mssqltoolsservice package name is retrieved from utility.py
utility.exec_command('pip install {}'.format(mssqltoolsservice_package_name), utility.ROOT_DIR)

print('Finished dev setup.')
