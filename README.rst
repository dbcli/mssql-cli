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

Installation
------------

.. code:: bash

    $ pip install mssql-cli

Please refer to the `installation guide`_ for detailed install instructions.

Usage
-----

Please refer to the `usage guide`_ for details on options and example usage.

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

Disclaimer for mssql_cli 0.0.3 users
----------------------------------------

For users of the older mssql_cli 0.0.3, please specifically download 0.0.3 as that version is no longer being maintained.

.. _mssql-cli: https://github.com/dbcli/mssql-cli
.. _dbcli.org community: https://github.com/dbcli
.. _installation guide: doc/installation_guide.md
.. _development guide: doc/development_guide.md
.. _usage guide: doc/usage_guide.md
.. _telemetry guide: doc/telemetry_guide.md
.. _Issues: https://github.com/dbcli/mssql-cli/issues
.. _Microsoft Open Source Code of Conduct: https://opensource.microsoft.com/codeofconduct/
.. _Code of Conduct FAQ: https://opensource.microsoft.com/codeofconduct/faq/
.. _BSD-3 license: https://github.com/dbcli/mssql-cli/blob/master/LICENSE.txt
