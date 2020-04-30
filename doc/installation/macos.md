# macOS Installation

## Requirements

### Supported OS Versions
mssql-cli supports macOS (x64) 10.12 and up.

### Python Installation
Although Python 2.7 is bundled with macOS, it is recommended to install Python 3, as version 2.7 has been officially deprecated by Python.

The latest Python installation may be downloaded from [Python's website](https://www.python.org/downloads/).

## Installing mssql-cli
> Note: your path to Python may be different from the listed command. For example, instead of `python` you may need to call `python3`.

mssql-cli is installed using `pip`. Use the instructions below if Python 3 is installed, or jump to the [next section](#python-27-installation) for Python 2.7:
```sh
# Install pip
sudo easy_install pip

# Update pip
python -m pip install --upgrade pip

# Install mssql-cli
sudo pip install mssql-cli

# Run mssql-cli
mssql-cli
```

## Uninstalling mssql-cli
Use `pip` to remove mssql-cli:
```sh
sudo pip uninstall mssql-cli
```
