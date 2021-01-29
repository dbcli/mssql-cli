#!/usr/bin/env python
from __future__ import print_function

import os
import sys
import utility

PYTHON = os.getenv('CUSTOM_PYTHON', sys.executable)

print('Running dev setup...')
print('Root directory \'%s\'\n' % utility.ROOT_DIR)

# install general requirements.
utility.exec_command('%s -m pip install --no-cache-dir -r requirements-dev.txt' % PYTHON,
                     utility.ROOT_DIR)

import mssqlcli.mssqltoolsservice.externals as mssqltoolsservice

# download the sqltoolssevice binaries for all platforms
mssqltoolsservice.download_sqltoolsservice_binaries()

# install mssqltoolsservice if this platform supports it.
utility.copy_current_platform_mssqltoolsservice()

print('Finished dev setup.')
