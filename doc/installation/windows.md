# Windows Installation

## Supported OS versions:
* Windows (x86/x64) 8.1 
* Windows (x86/x64) 10 
* Windows Server 2012+

Python is required for installation of mssql-cli and is not installed by default on Windows. To install Python, follow these instructions:
1. Open the latest Python installer package from [here](https://www.python.org/downloads/).
2. Select **Add Python [Version] to PATH** option before installation. Python must be in the PATH environment variable.
3. Install Python.

**Note:** If Python was installed into the "Program Files" directory, you may need to open the command prompt as an administrator for the above command to succeed.

Once Python is installed and in the PATH environment variable, open a command prompt, and install mssql-cli using the below command.

## Installation via pip
```shell
C:\> pip install mssql-cli
```
Or, use the following command if you encounter a launcher error:
```shell
C:\> python -m pip install mssql-cli
```

## Installation with daily preview build
Daily preview builds are dropped in our storage account. To install the latest available version of mssql-cli, use the below command:
```shell
C:\> pip install --pre --no-cache --extra-index-url https://mssqlcli.blob.core.windows.net/daily/whl mssql-cli
```

## Uninstallation via pip
```shell
C:\> pip uninstall mssql-cli
```

## Installation behind a proxy
Set two environment variables:
```shell
C:\>set http_proxy=domain\username:password@proxy_server:port
C:\>set https_proxy=domain\username:password@proxy_server:port
```
If the Password contains special characters like @,$,! (e.g. Password: P@ssword) then replace the special characters by their hex code equivalents with % prefix like this:
@==>%40
$==>%24
!==>%21
Example: username:p%40ssword@proxy_server:port

after this steps try install again

```shell
C:\>pip install mssql-cli
```
