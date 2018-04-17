.. image:: https://badge.fury.io/py/mssql_cli.svg
    :target: https://pypi.python.org/pypi/mssql_cli

.. image:: https://img.shields.io/pypi/pyversions/mssql-cli.svg
    :target: https://github.com/dbcli/mssql-cli

mssql-cli
===============


We’re excited to introduce `mssql-cli`_, a new and interactive command line query tool for SQL Server. This open source tool works cross-platform and proud to be a part of the `dbcli.org community`_. 

.. image:: screenshots/mssql-cli-autocomplete.gif
   :align: center


Features
------------
- Auto-completion
- Syntax highlighting
- Query history
- Configuration file support 
- Multi-line queries

Get mssql-cli
-------------

+--------------------------------------------+--------------------------------+-------------------------------+-------------------------------+
| Supported Platform                         | Downloads (stable)             | Downloads (preview)           | How to Install                |
+============================================+================================+===============================+===============================+
|  Windows (x64)                             | `.whl windows (x64)`_          | `.whl windows (x64) (dev)`_   | `Install on windows`_         |
+--------------------------------------------+--------------------------------+-------------------------------+-------------------------------+
|  Windows (x86)                             | `.whl windows (x86)`_          | `.whl windows (x86) (dev)`_   | `Install on windows`_         |
+--------------------------------------------+--------------------------------+-------------------------------+-------------------------------+
|  macOS 10.12+                              | `.whl`_                        | `.whl (dev)`_                 | `Install on macos`_           |
+--------------------------------------------+--------------------------------+-------------------------------+-------------------------------+
|  Ubuntu 17.04                              | `.deb`_                        | `.deb (dev)`_                 | `Install on ubuntu17`_        |
+--------------------------------------------+--------------------------------+-------------------------------+-------------------------------+
|  Ubuntu 16.04                              | `.deb`_                        | `.deb (dev)`_                 | `Install on ubuntu16`_        |
+--------------------------------------------+--------------------------------+-------------------------------+-------------------------------+
|  Ubuntu 14.04                              | `.deb`_                        | `.deb (dev)`_                 | `Install on ubuntu14`_        |
+--------------------------------------------+--------------------------------+-------------------------------+-------------------------------+
|  Debian 8.7+                               | `.deb`_                        | `.deb (dev)`_                 | `Install on debian8`_         |
+--------------------------------------------+--------------------------------+-------------------------------+-------------------------------+
|  Debian 9                                  | `.deb`_                        | `.deb (dev)`_                 | `Install on debian9`_         |
+--------------------------------------------+--------------------------------+-------------------------------+-------------------------------+
|  CentOS 7                                  | `.rpm`_                        | `.rpm (dev)`_                 | `Install on centos`_          |
+--------------------------------------------+--------------------------------+-------------------------------+-------------------------------+
|  Red Hat Enterprise Linux 7                | `.rpm`_                        | `.rpm (dev)`_                 | `Install on rhel7`_           |
+--------------------------------------------+--------------------------------+-------------------------------+-------------------------------+
|  OpenSUSE 42.2+                            | `.rpm`_                        | `.rpm (dev)`_                 | `Install on opensuse42`_      |
+--------------------------------------------+--------------------------------+-------------------------------+-------------------------------+
|  Fedora 25                                 | `.rpm`_                        | `.rpm (dev)`_                 | `Install on fedora25`_        |
+--------------------------------------------+--------------------------------+-------------------------------+-------------------------------+
|  Fedora 26                                 | `.rpm`_                        | `.rpm (dev)`_                 | `Install on fedora26`_        |
+--------------------------------------------+--------------------------------+-------------------------------+-------------------------------+


Installation via apt, yum
-------------------------
Please refer to `Get mssql-cli`_ for detailed install instructions per platform.


Installation via pip
--------------------

.. code:: bash

    $ pip install mssql-cli

Please refer to `Install via pip`_ for detailed install instructions via pip on each platform


Usage
-----

Please refer to the `usage guide`_ for details on options and example usage. If you are having any issues using mssql-cli, please see the `troubleshooting guide`_.

For general help content, pass in the ``-h`` parameter:

.. code:: bash

    $ mssql-cli --help

The mssql-cli tool includes a telemetry feature.  Please refer to the `telemetry guide`_ for more information.

Contributing
-----------------------------
If you would like to contribute to the project, please refer to the `development guide`_.

Reporting issues and feedback
-----------------------------

If you encounter any bugs with the tool please file an issue in the
`Issues`_ section of our GitHub repo.

Code of Conduct
---------------

This project has adopted the `Microsoft Open Source Code of Conduct`_. For more information see the `Code of Conduct FAQ`_ or contact
opencode@microsoft.com with any additional questions or comments.

License
-------

mssql-cli is licensed under the `BSD-3 license`_.

.. _mssql-cli: https://github.com/dbcli/mssql-cli
.. _dbcli.org community: https://github.com/dbcli
.. _troubleshooting guide: https://github.com/dbcli/mssql-cli/blob/master/doc/troubleshooting_guide.md
.. _development guide: https://github.com/dbcli/mssql-cli/tree/master/doc/development_guide.md
.. _usage guide: https://github.com/dbcli/mssql-cli/tree/master/doc/usage_guide.md
.. _telemetry guide: https://github.com/dbcli/mssql-cli/tree/master/doc/telemetry_guide.md
.. _Issues: https://github.com/dbcli/mssql-cli/issues
.. _Microsoft Open Source Code of Conduct: https://opensource.microsoft.com/codeofconduct/
.. _Code of Conduct FAQ: https://opensource.microsoft.com/codeofconduct/faq/
.. _BSD-3 license: https://github.com/dbcli/mssql-cli/blob/master/LICENSE.txt

.. _Install via pip: https://github.com/dbcli/mssql-cli/blob/tree/master/docs/installation/pip.md

.. _Install on windows: https://github.com/dbcli/mssql-cli/tree/master/docs/installation/windows.md#windows-installation
.. _Install on macos: https://github.com/dbcli/mssql-cli/tree/master/docs/installation/macos.md#macos-installation
.. _Install on ubuntu14: https://github.com/dbcli/mssql-cli/tree/master/docs/installation/linux.md#ubuntu-1404
.. _Install on ubuntu16: https://github.com/dbcli/mssql-cli/tree/master/docs/installation/linux.md#ubuntu-1604
.. _Install on ubuntu17: https://github.com/dbcli/mssql-cli/tree/master/docs/installation/linux.md#ubuntu-1704
.. _Install on debian8: https://github.com/dbcli/mssql-cli/tree/master/docs/installation/linux.md#debian-8
.. _Install on debian9: https://github.com/dbcli/mssql-cli/tree/master/docs/installation/linux.md#debian-9
.. _Install on centos: https://github.com/dbcli/mssql-cli/tree/master/docs/installation/linux.md#centos-7
.. _Install on rhel7: https://github.com/dbcli/mssql-cli/tree/master/docs/installation/linux.md#red-hat-enterprise-linux-rhel-7
.. _Install on opensuse42: https://github.com/dbcli/mssql-clidbcli/mssql-cli/tree/master/docs/installation/linux.md#opensuse-422
.. _Install on fedora25: https://github.com/dbcli/mssql-cli/tree/master/docs/installation/linux.md#fedora-25
.. _Install on fedora26: https://github.com/dbcli/mssql-cli/tree/master/docs/installation/linux.md#fedora-26

.. _.whl windows (x64) (dev): https://mssqlcli.blob.core.windows.net/daily/whl/mssql-cli/mssql_cli-dev-latest-py2.py3-none-win_amd64.whl
.. _.whl windows (x86) (dev): https://mssqlcli.blob.core.windows.net/daily/whl/mssql-cli/mssql_cli-dev-latest-py2.py3-none-win32.whl
.. _.whl (dev): https://mssqlcli.blob.core.windows.net/daily/whl/mssql-cli/mssql_cli-dev-latest-py2.py3-none-macosx_10_11_intel.whl

.. _.deb (dev): https://mssqlcli.blob.core.windows.net/daily/deb/mssql-cli-dev-latest.deb
.. _.rpm (dev): https://mssqlcli.blob.core.windows.net/daily/rpm/mssql-cli-dev-latest.rpm

.. _.deb: https://packages.microsoft.com/ubuntu/14.04/prod/pool/main/m/mssql-cli/mssql-cli_0.10.0-1_all.deb
.. _.rpm: https://packages.microsoft.com/rhel/7/prod/mssql-cli-0.10.0-1.el7.x86_64.rpm

.. _.whl windows (x64): https://files.pythonhosted.org/packages/0d/7c/5e2bcbed3d6215196118337aec9793a7d74ab5cca10b1d834873cb6ac492/mssql_cli-0.10.0-py2.py3-none-win_amd64.whl
.. _.whl windows (x86): https://files.pythonhosted.org/packages/4c/84/ba083d0677641f70ed11394fa93414275598161d1e8b6f444b67533079fa/mssql_cli-0.10.0-py2.py3-none-win32.whl
.. _.whl: https://files.pythonhosted.org/packages/a6/de/55b73b6aa03e9890585ef5df5dac5717708db1a5018acde2582526b42fc9/mssql_cli-0.10.0-py2.py3-none-macosx_10_11_intel.whl