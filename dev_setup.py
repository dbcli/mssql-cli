#!/usr/bin/env python
from __future__ import print_function
import os
import utility
import mssqlcli.mssqltoolsservice.externals as mssqltoolsservice

PIP = os.getenv('CUSTOM_PIP', 'pip')

print('Running dev setup...')
print('Root directory \'%s\'\n' % utility.ROOT_DIR)

# install general requirements.
utility.exec_command('%s install --no-cache-dir -r requirements-dev.txt' % PIP,
                     utility.ROOT_DIR)


# download the sqltoolssevice binaries for all platforms
mssqltoolsservice.download_sqltoolsservice_binaries()

# install mssqltoolsservice if this platform supports it.
utility.copy_current_platform_mssqltoolsservice()

print('Finished dev setup.')
