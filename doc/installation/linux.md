# Package Installation Instructions

Supports:

- [Ubuntu 14.04][u14]
- [Ubuntu 16.04][u16]
- [Ubuntu 17.04][u17]
- [Debian 8][deb8]
- [Debian 9][deb9]
- [CentOS 7][cos]
- [Red Hat Enterprise Linux (RHEL) 7][rhel7]
- [OpenSUSE 42.2][opensuse]
- [Fedora 25][fed25]
- [Fedora 26][fed26]

[downloads]:https://github.com/dbcli/mssql-cli/tree/master#get-mssql-cli

Once the package is installed, run `mssql-cli` from a terminal.

[u14]: #ubuntu-1404
[u16]: #ubuntu-1604
[u17]: #ubuntu-1704
[deb8]: #debian-8
[deb9]: #debian-9
[cos]: #centos-7
[rhel7]: #red-hat-enterprise-linux-rhel-7
[opensuse]: #opensuse-422
[fed25]: #fedora-25
[fed26]: #fedora-26

## Ubuntu 14.04

### Installation for latest stable version via Package Repository - Ubuntu 14.04

mssql-cli, for Linux, is published to package repositories for easy installation (and updates).
This is the preferred method.

```sh
# Import the public repository GPG keys
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -

# Register the Microsoft Ubuntu repository
sudo curl -o /etc/apt/sources.list.d/microsoft.list https://packages.microsoft.com/config/ubuntu/14.04/prod.list

# Update the list of products
sudo apt-get update

# Install mssql-cli
sudo apt-get install mssql-cli

# Start mssql-cli
mssql-cli
```

After registering the Microsoft repository once as superuser,
from then on, you just need to use `sudo apt-get upgrade mssql-cli` to update it.

### Installation for latest preview version via Direct Download - Ubuntu 14.04

Download the Debian package
`mssql-cli-dev-latest.deb`
from the [downloads] page onto the Ubuntu machine.

Then execute the following in the terminal:

```sh
sudo dpkg -i mssql-cli-dev-latest.deb
sudo apt-get install -f
```

> Please note that `dpkg -i` will fail with unmet dependencies;
> the next command, `apt-get install -f` resolves these
> and then finishes configuring the mssql-cli package.

### Uninstallation - Ubuntu 14.04

```sh
sudo apt-get remove mssql-cli
```

## Ubuntu 16.04

### Installation for latest stable version via Package Repository - Ubuntu 16.04

mssql-cli, for Linux, is published to package repositories for easy installation (and updates).
This is the preferred method.

```sh
# Import the public repository GPG keys
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -

# Register the Microsoft Ubuntu repository
sudo curl -o /etc/apt/sources.list.d/microsoft.list https://packages.microsoft.com/config/ubuntu/16.04/prod.list

# Update the list of products
sudo apt-get update

# Install mssql-cli
sudo apt-get install mssql-cli

# Start mssql-cli
mssql-cli
```

After registering the Microsoft repository once as superuser,
from then on, you just need to use `sudo apt-get upgrade mssql-cli` to update it.

### Installation for latest preview version  via Direct Download - Ubuntu 16.04

Download the Debian package
`mssql-cli-dev-latest.deb`
from the [downloads] page onto the Ubuntu machine.

Then execute the following in the terminal:

```sh
sudo dpkg -i mssql-cli-dev-latest.deb
sudo apt-get install -f
```

> Please note that `dpkg -i` will fail with unmet dependencies;
> the next command, `apt-get install -f` resolves these
> and then finishes configuring the mssql-cli package.

### Uninstallation - Ubuntu 16.04

```sh
sudo apt-get remove mssql-cli
```

## Ubuntu 17.04

### Installation for latest stable version via Package Repository - Ubuntu 17.04
mssql-cli, for Linux, is published to package repositories for easy installation (and updates).
This is the preferred method.

```sh
# Import the public repository GPG keys
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -

# Register the Microsoft Ubuntu repository
sudo curl -o /etc/apt/sources.list.d/microsoft.list https://packages.microsoft.com/config/ubuntu/17.04/prod.list

# Update the list of products
sudo apt-get update

# Install mssql-cli
sudo apt-get install mssql-cli

# Start mssql-cli
mssql-cli
```

After registering the Microsoft repository once as superuser,
from then on, you just need to use `sudo apt-get upgrade mssql-cli` to update it.

### Installation for latest preview version via Direct Download - Ubuntu 17.04

Download the Debian package
`mssql-cli-dev-latest.deb`
from the [downloads] page onto the Ubuntu machine.

Then execute the following in the terminal:

```sh
sudo dpkg -i mssql-cli-dev-latest.deb
sudo apt-get install -f
```

> Please note that `dpkg -i` will fail with unmet dependencies;
> the next command, `apt-get install -f` resolves these
> and then finishes configuring the mssql-cli package.

### Uninstallation - Ubuntu 17.04

```sh
sudo apt-get remove mssql-cli
```

## Debian 8.7

### Installation for latest stable version via Package Repository - Debian 8.7

mssql-cli, for Linux, is published to package repositories for easy installation (and updates).
This is the preferred method.

```sh
# Install system components
sudo apt-get update
sudo apt-get install curl apt-transport-https

# Import the public repository GPG keys
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -

# Register the Microsoft Product feed
sudo add-apt-repository "$(wget -qO- https://packages.microsoft.com/config/debian/8/prod.list)"

# Update the list of products
sudo apt-get update

# Install mssql-cli
sudo apt-get install mssql-cli

# Start mssql-cli
mssql-cli
```

After registering the Microsoft repository once as superuser,
from then on, you just need to use `sudo apt-get upgrade mssql-cli` to update it.

### Installation for latest preview version via Direct Download - Debian 8

Download the Debian package
`mssql-cli-dev-latest.deb`
from the [downloads] page onto the Debian machine.

Then execute the following in the terminal:

```sh
sudo dpkg -i mssql-cli-dev-latest.deb
sudo apt-get install -f
```

> Please note that `dpkg -i` will fail with unmet dependencies;
> the next command, `apt-get install -f` resolves these
> and then finishes configuring the mssql-cli package.

### Uninstallation - Debian 8

```sh
sudo apt-get remove mssql-cli
```

## Debian 9

### Installation for latest stable version via Package Repository - Debian 9

mssql-cli, for Linux, is published to package repositories for easy installation (and updates).
This is the preferred method.

```sh
# Import the public repository GPG keys
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -

# Register the Microsoft Product feed
sudo add-apt-repository "$(wget -qO- https://packages.microsoft.com/config/debian/8/prod.list)"

# Update the list of products
sudo apt-get update

# Install mssql-cli
sudo apt-get install mssql-cli

# Start mssql-cli
mssql-cli
```

After registering the Microsoft repository once as superuser,
from then on, you just need to use `sudo apt-get upgrade mssql-cli` to update it.

### Installation for latest preview version via Direct Download - Debian 9

Download the Debian package
`mssql-cli-dev-latest.deb`
from the [downloads] page onto the Debian machine.

Then execute the following in the terminal:

```sh
sudo dpkg -i mssql-cli-dev-latest.deb
sudo apt-get install -f
```

> Please note that `dpkg -i` will fail with unmet dependencies;
> the next command, `apt-get install -f` resolves these
> and then finishes configuring the mssql-cli package.

### Uninstallation - Debian 9

```sh
sudo apt-get remove mssql-cli
```

## CentOS 7

> This package also works on Oracle Linux 7.

### Installation for latest stable version via Package Repository (preferred) - CentOS 7

mssql-cli for Linux is published to official Microsoft repositories for easy installation (and updates).

```sh
# Register the Microsoft RedHat repository
sudo curl -o /etc/yum.repos.d/mssql-cli.repo https://packages.microsoft.com/config/rhel/7/prod.repo

# Install mssql-cli
sudo yum install mssql-cli

# Start mssql-cli
mssql-cli
```

After registering the Microsoft repository once as superuser,
you just need to use `sudo yum update mssql-cli` to update mssql-cli.

### Installation for latest preview version via Direct Download - CentOS 7

Using [CentOS 7][], download the RPM package
`mssql-cli-dev-latest.rpm`
from the [downloads] page onto the CentOS machine.

Then execute the following in the terminal:

```sh
sudo yum install mssql-cli-dev-latest.rpm
```

You can also install the RPM without the intermediate step of downloading it:

```sh
sudo yum install https://mssqlcli.blob.core.windows.net/daily/rpm/mssql-cli-dev-latest.rpm
```

### Uninstallation - CentOS 7

```sh
sudo yum remove mssql-cli
```

[CentOS 7]: https://www.centos.org/download/

## Red Hat Enterprise Linux (RHEL) 7

### Installation for latest stable version via Package Repository (preferred) - Red Hat Enterprise Linux (RHEL) 7

mssql-cli for Linux is published to official Microsoft repositories for easy installation (and updates).

```sh
# Register the Microsoft RedHat repository
curl https://packages.microsoft.com/config/rhel/7/prod.repo | sudo tee /etc/yum.repos.d/microsoft.repo

# Install mssql-cli
sudo yum install mssql-cli

# Start mssql-cli
mssql-cli
```

After registering the Microsoft repository once as superuser,
you just need to use `sudo yum update mssql-cli` to update mssql-cli.

### Installation for latest preview version via Direct Download - Red Hat Enterprise Linux (RHEL) 7

Download the RPM package
`mssql-cli-dev-latest.rpm`
from the [downloads] page onto the Red Hat Enterprise Linux machine.

Then execute the following in the terminal:

```sh
sudo yum install mssql-cli-dev-latest.rpm
```

You can also install the RPM without the intermediate step of downloading it:

```sh
sudo yum install https://mssqlcli.blob.core.windows.net/daily/rpm/mssql-cli-dev-latest.rpm
```

### Uninstallation - Red Hat Enterprise Linux (RHEL) 7

```sh
sudo yum remove mssql-cli
```

## OpenSUSE 42.2

### Installation for latest stable version via Package Repository (preferred) - OpenSUSE 42.2

mssql-cli for Linux is published to official Microsoft repositories for easy installation (and updates).

```sh
# Add the Microsoft Product feed
sudo zypper addrepo -fc https://packages.microsoft.com/config/opensuse/12/prod.repo

# Refresh the keys
sudo zypper --gpg-auto-import-keys refresh 

# Update the list of products
sudo zypper update

# Install mssql-cli
sudo zypper install mssql-cli

# Start mssql-cli
mssql-cli
```

### Installation for latest preview version via Direct Download - OpenSUSE 42.2

Download the RPM package `mssql-cli-dev-latest.rpm`
from the [downloads] page onto the OpenSUSE machine.

```sh
sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc
sudo zypper install mssql-cli-dev-latest.rpm
```

You can also install the RPM without the intermediate step of downloading it:

```sh
sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc
sudo zypper install https://mssqlcli.blob.core.windows.net/daily/rpm/mssql-cli-dev-latest.rpm
```

### Uninstallation - OpenSUSE 42.2

```sh
sudo zypper remove mssql-cli
```

## Fedora 25

### Installation for latest stable version via Package Repository (preferred) - Fedora 25

mssql-cli for Linux is published to official Microsoft repositories for easy installation (and updates).

```sh
# Register the Microsoft RedHat repository
sudo curl -o /etc/yum.repos.d/mssql-cli.repo https://packages.microsoft.com/config/rhel/7/prod.repo

# Update the list of products
sudo dnf update

# Install mssql-cli
sudo dnf install mssql-cli

# Start mssql-cli
mssql-cli
```

### Installation for latest preview version via Direct Download - Fedora 25

Download the RPM package
`mssql-cli-dev-latest.rpm`
from the [downloads] page onto the Fedora machine.

Then execute the following in the terminal:

```sh
sudo dnf install mssql-cli-dev-latest.rpm
```

You can also install the RPM without the intermediate step of downloading it:

```sh
sudo dnf install https://mssqlcli.blob.core.windows.net/daily/rpm/mssql-cli-dev-latest.rpm
```

### Uninstallation - Fedora 25

```sh
sudo dnf remove mssql-cli
```

## Fedora 26

### Installation for latest stable version via Package Repository (preferred) - Fedora 26

mssql-cli for Linux is published to official Microsoft repositories for easy installation (and updates).

```sh
# Register the Microsoft RedHat repository
sudo curl -o /etc/yum.repos.d/mssql-cli.repo https://packages.microsoft.com/config/rhel/7/prod.repo

# Update the list of products
sudo dnf update

# Install mssql-cli
sudo dnf install mssql-cli

# Start mssql-cli
mssql-cli
```

### Installation for latest preview version via Direct Download - Fedora 26

Download the RPM package
`mssql-cli-dev-latest.rpm`
from the [downloads] page onto the Fedora machine.

Then execute the following in the terminal:

```sh
sudo dnf update
sudo dnf install mssql-cli-dev-latest.rpm
```

You can also install the RPM without the intermediate step of downloading it:

```sh
sudo dnf update
sudo dnf install https://mssqlcli.blob.core.windows.net/daily/rpm/mssql-cli-dev-latest.rpm
```

### Uninstallation - Fedora 26

```sh
sudo dnf remove mssql-cli
```


