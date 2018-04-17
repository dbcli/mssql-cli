# Windows Installation

## Supported OS versions:
* Windows (x86/x64) 8.1 
* Windows (x86/x64) 10 
* Windows Server 2012+

Python is not installed by default on Windows.  The latest Python installation package can be downloaded from [here](https://www.python.org/downloads/).  When installing, select the 'Add Python to PATH' option.  Python must be in the PATH environment variable.
NOTE: If Python was installed into the "Program Files" directory, you may need to open the command prompt as an administrator for the above command to succeed.
Once Python is installed and in the PATH environment variable, open a command prompt, and install mssql-cli using the below command.  

For detailed i
## Installation via pip
```shell
C:\> pip install mssql-cli
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
