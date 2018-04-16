# macOS Installation

## Installation via Pip
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
```shell
# Install pip
$ sudo easy_install pip

# Update pip
$ sudo pip install --upgrade pip

# Install latest preview build of mssql-cli
$ sudo pip install --pre --no-cache --extra-index-url https://mssqlcli.blob.core.windows.net/daily/whl mssql-cli
```

## Uninstallation via Pip
```shell
$ sudo pip uninstall mssql-cli
```