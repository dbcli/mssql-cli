## Official Installation of mssql-cli

Follow the instructions link for your platform for the official instructions.

| Supported Platform                         |How to Install                |
|--------------------------------------------|------------------------------|
|  Windows (x64)                             |[Instructions][in-windows]    |
|  Windows (x86)                             |[Instructions][in-windows]    |
|  macOS 10.12+                              |[Instructions][in-macos]      |
|  Ubuntu 17.04                              |[Instructions][in-ubuntu17]   |
|  Ubuntu 16.04                              |[Instructions][in-ubuntu16]   |
|  Ubuntu 14.04                              |[Instructions][in-ubuntu14]   |
|  Debian 8.7+                               |[Instructions][in-debian8]    |
|  Debian 9                                  |[Instructions][in-debian9]    |
|  CentOS 7                                  |[Instructions][in-centos]     |
|  Red Hat Enterprise Linux 7                |[Instructions][in-rhel7]      |
|  OpenSUSE 42.2+                            |[Instructions][in-opensuse42] |
|  SUSE Enterprise Linux (SLES) 12           |[Instructions][in-sles12]     |
|  Fedora 25                                 |[Instructions][in-fedora25]   |
|  Fedora 26                                 |[Instructions][in-fedora26]   |

[in-windows]: https://github.com/dbcli/mssql-cli/blob/master/doc/installation/windows.md#windows-installation
[in-macos]: https://github.com/dbcli/mssql-cli/blob/master/doc/installation/macos.md#macos-installation
[in-ubuntu14]: https://github.com/dbcli/mssql-cli/blob/master/doc/installation/linux.md#ubuntu-1404
[in-ubuntu16]: https://github.com/dbcli/mssql-cli/blob/master/doc/installation/linux.md#ubuntu-1604
[in-ubuntu17]: https://github.com/dbcli/mssql-cli/blob/master/doc/installation/linux.md#ubuntu-1704
[in-debian8]: https://github.com/dbcli/mssql-cli/blob/master/doc/installation/linux.md#debian-8
[in-debian9]: https://github.com/dbcli/mssql-cli/blob/master/doc/installation/linux.md#debian-9
[in-centos]: https://github.com/dbcli/mssql-cli/blob/master/doc/installation/linux.md#centos-7
[in-rhel7]: https://github.com/dbcli/mssql-cli/blob/master/doc/installation/linux.md#red-hat-enterprise-linux-rhel-7
[in-opensuse42]: https://github.com/dbcli/mssql-cli/blob/master/doc/installation/linux.md#opensuse-422
[in-sles12]: https://github.com/dbcli/mssql-cli/blob/master/doc/installation/linux.md#sles-12
[in-fedora25]: https://github.com/dbcli/mssql-cli/blob/master/doc/installation/linux.md#fedora-25
[in-fedora26]: https://github.com/dbcli/mssql-cli/blob/master/doc/installation/linux.md#fedora-26


## Direct Downloads

The instructions above are the preferred installation method. Direct downloads are provided as an alternative in the 
scenario that your machine may not have access to the Microsoft package repository. Instructions for direct downloads can
also be found in the links above.

| Supported Platform                         |Latest Stable                 |Latest dev               |
|--------------------------------------------|------------------------------|-------------------------|
|  Windows (x64)                             |[.whl][whl-win-x64]           |[.whl][whl-win-x64-daily]|
|  Windows (x86)                             |[.whl][whl-win-x86]           |[.whl][whl-win-x86-daily]|
|  macOS 10.12+                              |[.whl][whl-macos]             |[.whl][whl-macos-daily]  |
|  Ubuntu 17.04                              |[.deb][deb]                   |[.deb][deb-daily]        |
|  Ubuntu 16.04                              |[.deb][deb]                   |[.deb][deb-daily]        |
|  Ubuntu 14.04                              |[.deb][deb]                   |[.deb][deb-daily]        |
|  Debian 8.7+                               |[.deb][deb]                   |[.deb][deb-daily]        |
|  Debian 9                                  |[.deb][deb]                   |[.deb][deb-daily]        |
|  CentOS 7                                  |[.rpm][rpm]                   |[.rpm][rpm-daily]        |
|  Red Hat Enterprise Linux 7                |[.rpm][rpm]                   |[.rpm][rpm-daily]        |
|  OpenSUSE 42.2+                            |[.rpm][rpm]                   |[.rpm][rpm-daily]        |
|  SUSE Enterprise Linux (SLES) 12           |[.rpm][rpm]                   |[.rpm][rpm-daily]        |
|  Fedora 25                                 |[.rpm][rpm]                   |[.rpm][rpm-daily]        |
|  Fedora 26                                 |[.rpm][rpm]                   |[.rpm][rpm-daily]        |

[whl-win-x64-daily]: https://mssqlcli.blob.core.windows.net/daily/whl/mssql-cli/mssql_cli-dev-latest-py2.py3-none-win_amd64.whl
[whl-win-x86-daily]: https://mssqlcli.blob.core.windows.net/daily/whl/mssql-cli/mssql_cli-dev-latest-py2.py3-none-win32.whl
[whl-macos-daily]: https://mssqlcli.blob.core.windows.net/daily/whl/mssql-cli/mssql_cli-dev-latest-py2.py3-none-macosx_10_11_intel.whl

[deb-daily]: https://mssqlcli.blob.core.windows.net/daily/deb/mssql-cli-dev-latest.deb
[rpm-daily]: https://mssqlcli.blob.core.windows.net/daily/rpm/mssql-cli-dev-latest.rpm

[deb]: https://packages.microsoft.com/ubuntu/14.04/prod/pool/main/m/mssql-cli/mssql-cli_0.14.0-1_all.deb
[rpm]: https://packages.microsoft.com/rhel/7/prod/mssql-cli-0.14.0-1.el7.x86_64.rpm
[whl-win-x64]: https://files.pythonhosted.org/packages/84/79/0c7344f20188ff1edf7d0124dd5a8e0004c01f7925729f670fa8b35ef761/mssql_cli-0.14.0-py2.py3-none-win_amd64.whl
[whl-win-x86]: https://files.pythonhosted.org/packages/65/e0/f20822df03394cbd6983e845b04f402569c0001e5082103a2ae1b7838c8d/mssql_cli-0.14.0-py2.py3-none-win32.whl
[whl-macos]: https://files.pythonhosted.org/packages/1f/d9/b12864cac848f6759d6b6b949535cdd8d8a32bdd5b735373e151bdf679c8/mssql_cli-0.14.0-py2.py3-none-macosx_10_11_intel.whl
