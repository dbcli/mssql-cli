# Linux Installation
Stable installations of mssql-cli on Linux are hosted in the [Microsoft Linux Software Repository](https://docs.microsoft.com/en-us/windows-server/administration/linux-package-repository-for-microsoft-software). mssql-cli supports the following Linux distributions:

[**Debian-based**](#Debian-based)
- [**Ubuntu**](#Ubuntu)
    - [Ubuntu 16.04 (Xenial)](#ubuntu-1604-Xenial)
    - [Ubuntu 18.04 (Bionic)](#ubuntu-1804-Bionic)
- [**Debian**](#Debian)
    - [Debian 8](#debian-8)
    - [Debian 9](#debian-9)

[**RPM-based**](#RPM-based)
- [**CentOS**](#CentOS)
    - [CentOS 7](#centos-7)
    - [CentOS 8](#centos-8)
- [**Red Hat Enterprise Linux**](#Red-Hat-Enterprise-Linux)
    - [RHEL 7](#RHEL-7)


## Debian-based

### Ubuntu

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

# Install missing dependencies
sudo apt-get install -f
```

#### Ubuntu 18.04 (Bionic)
```sh
# Import the public repository GPG keys
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -

# Register the Microsoft Ubuntu repository
sudo apt-add-repository https://packages.microsoft.com/ubuntu/18.04/prod

# Update the list of products
sudo apt-get update

# Install mssql-cli
sudo apt-get install mssql-cli

# Install missing dependencies
sudo apt-get install -f
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

# Install missing dependencies
sudo apt-get install -f
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

# Install missing dependencies
sudo apt-get install -f
```

### Upgrade on Ubuntu/Debian
After registering the Microsoft repository once as superuser,
from then on, you just need to use `sudo apt-get upgrade mssql-cli` to update it.

### Uninstall on Ubuntu/Debian
To uninstall mssql-cli, call `sudo apt-get remove mssql-cli`.


## RPM-based

### CentOS

#### CentOS 7
> This package also works on Oracle Linux 7.

```sh
# Import the public repository GPG keys
sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc

# Register the Microsoft product feed
sudo rpm -Uvh https://packages.microsoft.com/config/centos/7/packages-microsoft-prod.rpm

# Install dependencies and mssql-cli
sudo yum install libunwind
sudo yum install mssql-cli
```

#### CentOS 8
```sh
# Import the public repository GPG keys
sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc

# Register the Microsoft product feed
sudo rpm -Uvh https://packages.microsoft.com/config/centos/8/packages-microsoft-prod.rpm

# Install dependencies and mssql-cli
sudo yum install libunwind
sudo yum install mssql-cli
```

### Red Hat Enterprise Linux

#### RHEL 7
```sh
# Import the public repository GPG keys
sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc

# Register the Microsoft product feed
sudo rpm -Uvh https://packages.microsoft.com/config/rhel/7/packages-microsoft-prod.rpm

# Install dependencies and mssql-cli
sudo yum install libunwind
sudo yum install mssql-cli
```

### Upgrade on CentOS/RHEL
After registering the Microsoft repository once as superuser,
from then on, you just need to use `sudo yum update mssql-cli` to update it.

### Uninstall on CentOS/RHEL
To uninstall mssql-cli, call `sudo yum remove mssql-cli`.
