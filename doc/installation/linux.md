# Linux Installation
Stable installations of mssql-cli on Linux are hosted in the [Microsoft Linux Software Repository](https://docs.microsoft.com/en-us/windows-server/administration/linux-package-repository-for-microsoft-software).

mssql-cli supports the Linux distributions listed below. Docker instructions can be seen [here](https://github.com/dbcli/mssql-cli/blob/master/docker_environments/).

[**Debian-based**](#Debian-based)
- [**Ubuntu**](#Ubuntu)
    - [Ubuntu 14.04 (Trusty)](#ubuntu-1404-Trusty)
    - [Ubuntu 16.04 (Xenial)](#ubuntu-1604-Xenial)
- [**Debian**](#Debian)
    - [Debian 8](#debian-8)
    - [Debian 9](#debian-9)

[**RPM-based**](#RPM-based)
- [**CentOS/RHEL**](#CentOSRHEL)
    - [CentOS 7](#centos-7)
    - [Red Hat Enterprise Linux (RHEL) 7](#red-hat-enterprise-linux-rhel-7)
- [**openSUSE**](#opensuse)
    - [openSUSE 42.2](#opensuse-422)
- [**Fedora**](#fedora)
    - [Fedora 25](#fedora-25)
    - [Fedora 26](#fedora-26)


## Debian-based

### Ubuntu

#### Ubuntu 14.04 (Trusty)
```sh
# Import the public repository GPG keys
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -

# Register the Microsoft Ubuntu repository
sudo apt-add-repository https://packages.microsoft.com/ubuntu/14.04/prod

# Update the list of products
sudo apt-get update

# Install mssql-cli
sudo apt-get install mssql-cli
```

#### Ubuntu 16.04 (Xenial)
```sh
# Import the public repository GPG keys
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -

# Register the Microsoft Ubuntu repository
sudo apt-add-repository https://packages.microsoft.com/ubuntu/16.04/prod

# Update the list of products
sudo apt-get update

# Install mssql-cli
sudo apt-get install mssql-cli
```

### Debian
> `apt-transport-https` is required for importing keys. If not installed, call `sudo apt-get install curl apt-transport-https`.

#### Debian 8
```sh
# Import the public repository GPG keys
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -

# Register the Microsoft Product feed
echo "deb [arch=amd64] https://packages.microsoft.com/debian/8/prod jessie main" | sudo tee /etc/apt/sources.list.d/mssql-cli.list

# Update the list of products
sudo apt-get update

# Install mssql-cli
sudo apt-get install mssql-cli
```

#### Debian 9
```sh
# Import the public repository GPG keys
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -

# Register the Microsoft Product feed
echo "deb [arch=amd64] https://packages.microsoft.com/debian/9/prod stretch main" | sudo tee /etc/apt/sources.list.d/mssql-cli.list

# Update the list of products
sudo apt-get update

# Install mssql-cli
sudo apt-get install mssql-cli
```

### Upgrade on Ubuntu/Debian
After registering the Microsoft repository once as superuser,
from then on, you just need to use `sudo apt-get upgrade mssql-cli` to update it.

### Uninstall on Ubuntu/Debian
To uninstall mssql-cli, call `sudo apt-get remove mssql-cli`.


## RPM-based

### CentOS/RHEL

#### CentOS 7
> This package also works on Oracle Linux 7.

```sh
sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc
sudo curl -o /etc/yum.repos.d/mssql-cli.repo https://packages.microsoft.com/config/rhel/7/prod.repo
sudo yum install mssql-cli
```

#### Red Hat Enterprise Linux (RHEL) 7
```sh
sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc
curl https://packages.microsoft.com/config/rhel/7/prod.repo | sudo tee /etc/yum.repos.d/microsoft.repo
sudo yum install mssql-cli
```

### Upgrade on CentOS/RHEL
After registering the Microsoft repository once as superuser,
from then on, you just need to use `sudo yum update mssql-cli` to update it.

### Uninstall on CentOS/RHEL
To uninstall mssql-cli, call `sudo yum remove mssql-cli`.


## openSUSE

### openSUSE

#### openSUSE 42.2

mssql-cli for Linux is published to official Microsoft repositories for easy installation (and updates).

```sh
# Add openSUSE repository feed
sudo zypper addrepo https://download.opensuse.org/repositories/server:monitoring/openSUSE_Leap_42.2/server:monitoring.repo

# Add the Microsoft Product feed
sudo zypper addrepo -fc https://packages.microsoft.com/config/opensuse/42.2/prod.repo

# Add Microsoft repository key
sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc

# Update the list of products
sudo zypper update

# Install system level component and mssql-cli
sudo zypper install libffi-devel
sudo zypper install mssql-cli
```


## Fedora

### Fedora

#### Fedora 25

```sh
# Register the Microsoft RedHat repository
sudo curl -o /etc/yum.repos.d/mssql-cli.repo https://packages.microsoft.com/config/rhel/7/prod.repo

# Update the list of products
sudo dnf update

# Install mssql-cli
sudo dnf install mssql-cli
```

#### Fedora 26
```sh
# Register the Microsoft RedHat repository
sudo curl -o /etc/yum.repos.d/mssql-cli.repo https://packages.microsoft.com/config/rhel/7/prod.repo

# Update the list of products
sudo dnf update

# Install mssql-cli
sudo dnf install mssql-cli
```
