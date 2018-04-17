# pip installation guide
Installation via pip is supported, but will require .NET Core 2.0 dependencies to be installed prior.

The following chart shows the .NET Core 2.0 dependencies on different Linux distributions that are officially supported.
The pip installation steps will outline commands to execute to download and install the dependencies.

| OS                 | Dependencies |
| ------------------ | ------------ |
| Ubuntu 14.04       | libunwind8, libicu52 |
| Ubuntu 16.04       | libunwind8, libicu55 |
| Ubuntu 17.04       | libunwind8, libicu57 |
| Debian 8 (Jessie)  | libunwind8, libicu52 |
| Debian 9 (Stretch) | libunwind8, libicu57 |
| CentOS 7 <br> Oracle Linux 7 <br> RHEL 7 <br> OpenSUSE 42.2 <br> Fedora 25 | libunwind, libcurl, libicu |
| Fedora 26          | libunwind, libicu |

## Quick Start
mssql-cli needs Python to run, and works with Python 2.7 and 3.6.

mssql-cli is installed via pip.  If you know pip, you can install mssql-cli using command
```shell
$ pip install mssql-cli
```
This command may need to run as sudo if you are installing to the system site packages. mssql-cli can be
installed using the --user option, which does not require sudo.
```shell
$ pip install --user mssql-cli
```

If you are having installation issues, see the [troubleshooting](https://github.com/dbcli/mssql-cli/blob/master/doc/troubleshooting_guide.md) section for known issues and workarounds.


## Detailed Instructions

For supported operating system specific installations, see one of the following links:

* [Windows (x86/x64) 8.1, 10, Windows Server 2012+](#windows-installation)
* [macOS (x64) 10.12+](#macos-installation)
* [Linux (x64)](#linux-installation)
    * [Red Hat Enterprise Linux 7](#install-red-hat-enterprise-linux-rhel-7)
    * [CentOS 7](#install-centos-7)
    * [Fedora 25, Fedora 26](#install-fedora-25-fedora-26)
    * [Debian 8.7 or later versions](#install-debian-87-or-later)
    * [Ubuntu 17.04, Ubuntu 16.04, Ubuntu 14.04](#install-ubuntu-1704-ubuntu-1604-ubuntu-1404)
    * [Linux Mint 18, Linux Mint 17](#install-linux-mint-18-linux-mint-17)
    * [openSUSE 42.2 or later](#install-opensuse-422-or-later)
    * [SUSE Enterprise Linux (SLES) 12 SP2 or later](#install-suse-enterprise-linux-sles-12-sp2-or-later)

# Windows Installation

Python is not installed by default on Windows.  The latest Python installation package can be downloaded from [here](https://www.python.org/downloads/).  When installing, select the 'Add Python to PATH' option.  Python must be in the PATH environment variable.

Once Python is installed and in the PATH environment variable, open a command prompt, and install mssql-cli using the below command.  

```shell
C:\> pip install mssql-cli
```
NOTE: If Python was installed into the "Program Files" directory, you may need to open the command prompt as an administrator for the above command to succeed.

# macOS Installation

On macOS, Python 2.7 is generally pre-installed. You may have to upgrade pip with the following easy_install commands.

```shell
$ sudo easy_install pip
$ sudo pip install --upgrade pip
$ sudo pip install mssql-cli --ignore-installed six
```

# Linux Installation

On Linux, Python 2.7 is generally pre-installed. There are two prerequisite packages to run mssql-cli on Linux: libunwind and libicu.

## Install Red Hat Enterprise Linux (RHEL) 7
```shell
$ wget https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm 
$ sudo yum -y install ./epel-release-latest-7.noarch.rpm
$ sudo yum -y install icu libunwind python-pip 
$ sudo pip install mssql-cli
```

## Install CentOS 7
```shell
$ sudo yum -y install epel-release 
$ sudo yum -y install libunwind libicu python-pip 
$ sudo pip install mssql-cli
```

## Install Fedora 25, Fedora 26
```shell
$ dnf upgrade
$ dnf install libunwind libicu python-pip
$ sudo pip install mssql-cli
```

## Install Debian 8.7 or later
```shell
$ echo deb http://ftp.us.debian.org/debian jessie main | sudo tee -a /etc/apt/sources.list
$ sudo apt-get update & sudo apt-get install -y libunwind8 python-pip
$ sudo pip install --upgrade pip
$ sudo pip install mssql-cli
```

## Install Ubuntu 17.04, Ubuntu 16.04, Ubuntu 14.04

### Install Ubuntu 17.04
```shell
$ sudo apt-get update & sudo apt-get install -y libunwind8 python-pip libicu57
$ sudo pip install --upgrade pip
$ sudo pip install mssql-cli
```

### Install Ubuntu 16.04
```shell
$ sudo apt-get update & sudo apt-get install -y libunwind8 python-pip libicu55 
$ sudo pip install --upgrade pip
$ sudo pip install mssql-cli
```

### Install Ubuntu 14.04
```shell
$ sudo apt-get update & sudo apt-get install -y libunwind8 python-pip libicu52
$ sudo pip install --upgrade pip
$ sudo pip install mssql-cli
```

## Install Linux Mint 18, Linux Mint 17

### Install Linux Mint 18
```shell
$ sudo apt-get update & sudo apt-get install -y libunwind8 python-pip libicu57
$ sudo pip install --upgrade pip
$ sudo pip install mssql-cli
```

### Install Linux Mint 17
```shell
$ sudo apt-get update & sudo apt-get install -y libunwind8 python-pip libicu55
$ sudo pip install --upgrade pip
$ sudo pip install mssql-cli
```

### Install OpenSUSE 42.2 or later
```shell
$ sudo zypper update
$ sudo zypper install libunwind libicu python-pip
$ sudo pip install mssql-cli
```
 
 
### Install SUSE Enterprise Linux (SLES) 12 SP2 or later
```shell
$ sudo zypper update
$ sudo zypper install libunwind libicu python-pip
$ sudo pip install mssql-cli
```
