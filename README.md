[![PyPI](https://badge.fury.io/py/mssql-cli.svg)](https://pypi.python.org/pypi/mssql-cli)
[![Python 2.7|3.4|3.5|3.6|3.7|3.8](https://img.shields.io/badge/python-2.7&nbsp;|&nbsp;3.4&nbsp;|&nbsp;3.5&nbsp;|&nbsp;3.6&nbsp;|&nbsp;3.7&nbsp;|&nbsp;3.8-blue.svg)](https://github.com/dbcli/mssql-cli)

# mssql-cli
[**mssql-cli**](https://github.com/dbcli/mssql-cli) is an interactive command line query tool for SQL Server. This open source tool works cross-platform and proud to be a part of the [dbcli](github.com/dbcli) community. 

![mssql-cli Autocomplete](https://github.com/dbcli/mssql-cli/raw/master/screenshots/mssql-cli-autocomplete.gif)

mssql-cli supports a rich interactive command line experience, with features such as:
- **Auto-completion**: fewer keystrokes needed to complete complicated queries.
- **Syntax highlighting**: highlights T-SQL keywords.
- **Query history**: easily complete an auto-suggested query that was previously executed.
- **Configuration file support**: customize the mssql-cli experience for your needs.
- **Multi-line queries**: execute multiple queries at once using the multi-line edit mode.
- **Non-interactive support**: execute a query without jumping into the interactive experience.

## Quick Start
Read the section below to quickly get started with mssql-cli. Consult the [usage guide](https://github.com/dbcli/mssql-cli/tree/master/doc/usage_guide.md) for a deeper dive into mssql-cli features.

### Install mssql-cli
Platform-specific installation instructions are below:
| [Windows](https://github.com/dbcli/mssql-cli/blob/master/doc/installation/windows.md#windows-installation) | [macOS](https://github.com/dbcli/mssql-cli/blob/master/doc/installation/macos.md#macos-installation) | [Linux](https://github.com/dbcli/mssql-cli/blob/master/doc/installation/linux.md) |
| - | - | - |

Visit the [installation reference guide](https://github.com/dbcli/mssql-cli/tree/master/doc/installation) to view all supported releases and downloads.

#### Install with Linux Package Manager
Follow the [Linux installation instructions]('https://github.com/dbcli/mssql-cli/blob/master/doc/installation/linux.md') to install mssql-cli using `apt-get`, `yum`, and other Linux package managers.

#### Install with pip
```sh
python -m pip install mssql-cli
```
Please refer to the [pip installation docs](https://github.com/dbcli/mssql-cli/blob/master/doc/installation/pip.md) for more platform-specific information.

### Connect to Server
Complete the command below to connect to your server:
```sh
mssql-cli -S <server URL> -d <database name> -U <username> -P <password>
```

### Exit mssql-cli
Press **Ctrl+D** or type `quit`.

### Show Options
For general help content, pass in the `-h` parameter:
```sh
mssql-cli --help
```

### Usage Docs
Please refer to the [usage guide](https://github.com/dbcli/mssql-cli/tree/master/doc/usage_guide.md) for details on options and example usage. If you are having any issues using mssql-cli, please see the [troubleshooting guide](https://github.com/dbcli/mssql-cli/blob/master/doc/troubleshooting_guide.md).

## Telemetry
The mssql-cli tool includes a telemetry feature. Please refer to the [telemetry guide](https://github.com/dbcli/mssql-cli/tree/master/doc/telemetry_guide.md) for more information.

## Contributing
If you would like to contribute to the project, please refer to the [development guide](https://github.com/dbcli/mssql-cli/tree/master/doc/development_guide.md).

## Contact Us
If you encounter any bugs or would like to leave a feature request, please file an issue in the
[**Issues**](https://github.com/dbcli/mssql-cli/issues) section of our GitHub repo.

## Code of Conduct
This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact
opencode@microsoft.com with any additional questions or comments.

## License
mssql-cli is licensed under the [BSD-3 license](https://github.com/dbcli/mssql-cli/blob/master/LICENSE.txt).
