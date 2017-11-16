#!/usr/bin/env python
from __future__ import print_function
import utility
import pgcli.mssqltoolsservice.externals as mssqltoolsservice

print('Running dev setup...')
print('Root directory \'{}\'\n'.format(utility.ROOT_DIR))

# install general requirements.
utility.exec_command('pip install -r requirements-dev.txt', utility.ROOT_DIR)

# install mssqltoolsservice if this platform supports it.
run_time_id = utility.get_current_platform()

if run_time_id:
    mssqltoolsservice.copy_sqltoolsservice(run_time_id)
else:
    print("This platform does not support mssqltoolsservice.")

print('Finished dev setup.')
