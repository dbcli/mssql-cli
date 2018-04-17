# macOS Installation

## Supported OS versions:
* macOS (x64) 10.12+

## Installation via pip
On macOS, Python 2.7 is generally pre-installed. You may have to upgrade pip with the following easy_install commands.
```shell
# Install pip
$ sudo easy_install pip

# Update pip
$ sudo pip install --upgrade pip

# Install mssql-cli
$ sudo pip install mssql-cli --ignore-installed six

# Run mssql-cli
$ mssql-cli -h
```

## Installation with daily preview build
Daily preview builds are dropped in our storage account. To install the latest available version of mssql-cli, use the below command:
```shell
# Install pip
$ sudo easy_install pip

# Update pip
$ sudo pip install --upgrade pip

# Install latest preview build of mssql-cli
$ sudo pip install --pre --no-cache --extra-index-url https://mssqlcli.blob.core.windows.net/daily/whl mssql-cli
```

## Uninstallation via pip
```shell
$ sudo pip uninstall mssql-cli
```