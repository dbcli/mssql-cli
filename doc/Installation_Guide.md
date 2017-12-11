# Installation Guide

## Quick Start
mssql-cli is installed via pip.  If you know pip, you can install mssql-cli using command
```shell
$ pip install mssql-cli
```
This command may need to run as sudo if you are installing to the system site packages. mssql-cli can be
installed using the --user option, which does not require sudo.
```shell
$ pip install --user mssql-cli
```

If you are having installation issues, see the [troubleshooting](#troubleshooting) section for known issues and workarounds.


## Detailed Instructions

For operating system specific installations, see one of the following links:

* [Windows](#windows-installation)
* [macOS](#macos-installation)
* [Linux](#linux-installation)
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

Once Python is installed and in the PATH environment variable, open a command prompt, and install mssql-cli using the command:
```shell
C:\> pip install mssql-cli
```

# macOS Installation

To can install mssql-cli using the Homebrew package manager.

## Homebrew Installation

```shell
$ sudo brew install python
$ sudo pip install --upgrade pip
$ sudo pip install mssql-cli --ignore-installed six
```

# Linux Installation

There are two prerequisit packages to run mssql-cli on Linux: libunwind and libicu.

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
$ sudo  update
$ sudo install libunwind libicu
$ sudo pip install --upgrade pip
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

# Troubleshooting

If you're having installation issues, please check the below known issues and workarounds.  If you're having a different issue, please check the [issues](https://github.com/dbcli/mssql-cli/issues) page to see if the issue has already been reported.  If you don't see your issue there, filing a new issue would be appreciated.

## Error: No module named mssqlcli
If the installation was successful and this error message is encountered, this may be caused by different versions of python in the environment.
i.e Used python 3.6 to install mssql-cli, but PATH has python 2.7 so it uses the python 2.7 interpreter which has no visibility to packages installed into python 3.6.

The workaround to prevent this is to use a virtual environment, which will provide a isolated environment that is tied to a specific python version.
More information can be found at:

- [Virtual Environment Info](virtual_environment_info.md)

- [Development guide](development_guide.md#Environment_Setup)

## Error: Could not find version that satisfies the requirement mssql-cli
If you see the above error running `pip install mssql-cli`, this means the pip version used is out-of-date.  Please upgrade your pip installation for your python platform and OS distribution. 

## Error: System.DllNotFoundException: Unable to load DLL 'System.Security.Cryptography.Native': The specified module could not be found.
If you encounter this error on MacOS, this means you need the latest version of OpenSSL. Later version of macOS (Sierra, and High Sierra) should not have this issue.  To install OpenSSL use the following commands:
```shell
$ brew update
$ brew install openssl
$ mkdir -p /usr/local/lib
$ ln -s /usr/local/opt/openssl/lib/libcrypto.1.0.0.dylib /usr/local/lib/
$ ln -s /usr/local/opt/openssl/lib/libssl.1.0.0.dylib /usr/local/lib/
```

## Error: libunwind.so: cannot open shared object file
If you encounter the below error running mssql-cli, this means the libunwind package is not installed.  Please install the libunwind package for your Linux distribution.
```shell
Failed to load /usr/local/lib/python2.7/dist-packages/mssqltoolsservice/bin/libcoreclr.so, error
libunwind.so.8: cannot open shared object file: No such file or directory
```

## Error: Failed to initialize CoreCLR, HRESULT: 0x80131500
If you encounter the below error running mssql-cli, this means the libicu package is not installed.  Please install the libicu package for your Linux distribution.
```shell
Failed to initialize CoreCLR, HRESULT: 0x80131500
```
