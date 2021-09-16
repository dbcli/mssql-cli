# Windows Installation

## Requirements

### Supported OS Versions
mssql-cli is supported on Windows with:
* Windows (x86/x64) 8.1 
* Windows (x86/x64) 10 
* Windows Server 2012+

### Python Installation

Python is required for installation of mssql-cli and is not installed by default on Windows. To install Python, follow these instructions:
1. Open the latest Python installer package from [here](https://www.python.org/downloads/).
2. Select **Add Python [Version] to PATH** option before installation. Python must be in the PATH environment variable.
3. Install Python.

> If Python was installed into the "Program Files" directory, you may need to open the command prompt as an administrator for the above command to succeed.

Proceed to the next section once Python is installed and in the PATH environment variable.

## Installing mssql-cli
> Note: your path to Python may be different from the listed command. For example, instead of `python` you may need to call `python3`.

mssql-cli is installed using `pip` on Windows:
```sh
python -m pip install mssql-cli
```

## Uninstalling mssql-cli
Uninstall mssql-cli using `pip`:
```sh
pip uninstall mssql-cli
```

## Installation Behind a Proxy
Set two environment variables:
```sh
set http_proxy=domain\username:password@proxy_server:port
set https_proxy=domain\username:password@proxy_server:port
```
If the Password contains special characters like `@,$,!` (e.g. `password:PLACEHOLDER`) then replace the special characters by their hex code equivalents with `%` prefix, as exemplified below:
* `@`: `%40`
* `$`: `%24`
* `!`: `%21`

Example: `username:p%40ssword@proxy_server:port`

You may attempt installation after completing these steps:

```sh
pip install mssql-cli
```
