# Installation Guide

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

If you are having installation issues, see the [troubleshooting](#troubleshooting_guide.md) section for known issues and workarounds.


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

#apt
## Ubuntu 14.04
```shell
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
sudo add-apt-repository "$(wget -qO- https://packages.microsoft.com/config/ubuntu/14.04/prod.list)"
Sudo apt-get update
Sudo apt-get install mssql-cli
```
## Ubuntu 16.04
```shell
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
sudo add-apt-repository "$(wget -qO- https://packages.microsoft.com/config/ubuntu/16.04/prod.list)"
Sudo apt-get update
Sudo apt-get install mssql-cli
```
## Ubuntu 17.04
```shell
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
sudo add-apt-repository "$(wget -qO- https://packages.microsoft.com/config/ubuntu/17.04/prod.list)"
Sudo apt-get update
Sudo apt-get install mssql-cli
```

##Debian 8.7 or later
```shell
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
sudo add-apt-repository "$(wget -qO- https://packages.microsoft.com/config/debian/8/prod.list)"
Sudo apt-get update
Sudo apt-get install mssql-cli
```

#Yum
## Red Hat Enterprise Linux (RHEL) 7, Fedora 25 or 26
```shell
sudo curl -o /etc/yum.repos.d/mssql-cli.repo https://packages.microsoft.com/config/rhel/7/prod.repo
sudo yum install -y mssql-cli
```

## CentOS 7
```shell
sudo curl -o /etc/yum.repos.d/mssql-cli.repo https://packages.microsoft.com/config/centos/7/prod.repo
sudo yum install -y mssql-cli
```

#Zypper
##SUSE Enterprise Linux (SLES) 12 SP2 or later
```shell
sudo zypper addrepo -fc https://packages.microsoft.com/config/sles/12/prod.repo
sudo zypper --gpg-auto-import-keys refresh 
sudo zypper install -y mssql-cli
```
##openSUSE 42.2 or later
```shell
sudo zypper addrepo -fc https://packages.microsoft.com/config/opensuse/12/prod.repo
sudo zypper --gpg-auto-import-keys refresh 
sudo zypper install -y mssql-cli
```