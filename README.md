[![PyPI](https://badge.fury.io/py/mssql-cli.svg)](https://pypi.python.org/pypi/mssql-cli)
[![Python 2,3](https://img.shields.io/badge/python-2.7,&nbsp;3.x-blue.svg)](https://github.com/dbcli/mssql-cli)

# mssql-cli
[**mssql-cli**](https://github.com/dbcli/mssql-cli) is an interactive command line query tool for SQL Server. This open source tool works cross-platform and proud to be a part of the [**dbcli**](github.com/dbcli) community. 

![mssql-cli Autocomplete](https://github.com/dbcli/mssql-cli/raw/master/screenshots/mssql-cli-autocomplete.gif)

## Features
- Auto-completion
- Syntax highlighting
- Query history
- Configuration file support 
- Multi-line queries

## Install
Platform-specific installation instructions are below:
| [Windows](https://github.com/dbcli/mssql-cli/blob/master/doc/installation/windows.md#windows-installation) | [macOS](https://github.com/dbcli/mssql-cli/blob/master/doc/installation/macos.md#macos-installation) | [Linux](https://github.com/dbcli/mssql-cli/blob/master/doc/installation/linux.md) |
| - | - | - |

Please view the [official release guide](https://github.com/dbcli/mssql-cli/blob/master/doc/installation_guide.md) to view all supported releases.

### Install with pip
```
$ pip install mssql-cli
```
Please refer to the [pip installation docs](https://github.com/dbcli/mssql-cli/blob/master/doc/installation/pip.md) for more platform-specific information.

### Install with apt-get and yum
**A new stable version of mssql-cli is coming soon for `apt-get` and `yum`.**

Older versions of mssql-cli may be installed using `apt-get` or `yum` by following [these instructions]('https://github.com/dbcli/mssql-cli/blob/master/doc/installation/linux.md')

### Install Daily Builds
Direct downloads for both latest stable and preview bits can be found at [here](https://github.com/dbcli/mssql-cli/blob/master/doc/installation_guide.md#Direct-Downloads).


## Get mssql-cli
| Install Instructions              |
| --------------------------------- |
|  Windows (x64)                    |
|  Windows (x86)                    |
|  macOS 10.12+                     |
|  Ubuntu 17.04                     |
|  Ubuntu 16.04                     |
|  Ubuntu 14.04                     |
|  Debian 8.7                       |
|  Debian 9                         |
|  CentOS 7                         |
|  Red Hat Enterprise Linux 7       |
|  OpenSUSE 42.2                    |
|  Fedora 25                        |
|  Fedora 26                        |


### Direct downloads
Direct downloads for both latest stable and preview bits can be found at `Direct download`_.

### Installation via apt, yum
Please refer to `Get mssql-cli`_ for detailed install instructions per platform.


### Installation via pip
```
$ pip install mssql-cli
```
Please refer to `install via pip`_ for detailed install instructions via pip on each platform.


## Usage
Please refer to the [usage guide](https://github.com/dbcli/mssql-cli/tree/master/doc/usage_guide.md) for details on options and example usage. If you are having any issues using mssql-cli, please see the [troubleshooting guide](https://github.com/dbcli/mssql-cli/blob/master/doc/troubleshooting_guide.md).

For general help content, pass in the `-h` parameter:
```
$ mssql-cli --help
```
The mssql-cli tool includes a telemetry feature.  Please refer to the [telemetry guide](https://github.com/dbcli/mssql-cli/tree/master/doc/telemetry_guide.md) for more information.

### Configuration
Customization and persistence of settings can be achieved with a config file, whose path can be passed as the `--mssqlclirc <file>` command line argument. Otherwise it is read from the default path `~/.config/mssqlcli/config` on macOS and Linux, and `%LOCALAPPDATA%\dbcli\mssqlcli\config` on Windows. See the [config file](https://github.com/dbcli/mssql-cli/blob/master/mssqlcli/mssqlclirc) itself for a description of all available options.

## Contributing
If you would like to contribute to the project, please refer to the [development guide](https://github.com/dbcli/mssql-cli/tree/master/doc/development_guide.md).

## Reporting issues and feedback
If you encounter any bugs with the tool please file an issue in the
[**Issues**](https://github.com/dbcli/mssql-cli/issues) section of our GitHub repo.

## Code of Conduct
This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact
opencode@microsoft.com with any additional questions or comments.

## License
mssql-cli is licensed under the [BSD-3 license](https://github.com/dbcli/mssql-cli/blob/master/LICENSE.txt).
