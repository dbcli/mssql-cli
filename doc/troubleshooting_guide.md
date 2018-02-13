Troubleshooting Guide
========================================
## Table of Contents
1. [Installation Issues](#Installation_Issues)
2. [Usage Issues](#Usage_Issues)
3. [Reporting Issues](#Reporting_Issues)

## <a name="Installation_Issues"></a>Installation Issues:

If you're having installation issues, please check the below known issues and workarounds.  If you're having a different issue, please check the [issues](https://github.com/dbcli/mssql-cli/issues) page to see if the issue has already been reported.  If you don't see your issue there, filing a new issue would be appreciated.

### Error: No module named mssqlcli
If the installation was successful and this error message is encountered, this may be caused by different versions of python in the environment.
i.e Used python 3.6 to install mssql-cli, but PATH has python 2.7 so it uses the python 2.7 interpreter which has no visibility to packages installed into python 3.6.

The workaround to prevent this is to use a virtual environment, which will provide a isolated environment that is tied to a specific python version.
More information can be found at:

- [Virtual Environment Info](virtual_environment_info.md)

- [Development guide](development_guide.md#Environment_Setup)

### Error: Could not find version that satisfies the requirement mssql-cli
If you see the above error running `pip install mssql-cli`, this means the pip version used is out-of-date.  Please upgrade your pip installation for your python platform and OS distribution. 

### Error: System.DllNotFoundException: Unable to load DLL 'System.Security.Cryptography.Native': The specified module could not be found.
If you encounter this error on MacOS, this means you need the latest version of OpenSSL. Later version of macOS (Sierra, and High Sierra) should not have this issue.  To install OpenSSL use the following commands:
```shell
$ brew update
$ brew install openssl
$ mkdir -p /usr/local/lib
$ ln -s /usr/local/opt/openssl/lib/libcrypto.1.0.0.dylib /usr/local/lib/
$ ln -s /usr/local/opt/openssl/lib/libssl.1.0.0.dylib /usr/local/lib/
```

### Error: libunwind.so: cannot open shared object file
If you encounter the below error running mssql-cli, this means the libunwind package is not installed.  Please install the libunwind package for your Linux distribution.
```shell
Failed to load /usr/local/lib/python2.7/dist-packages/mssqltoolsservice/bin/libcoreclr.so, error
libunwind.so.8: cannot open shared object file: No such file or directory
```

### Error: Failed to initialize CoreCLR, HRESULT: 0x80131500
If you encounter the below error running mssql-cli, this means the libicu package is not installed.  Please install the libicu package for your Linux distribution.
```shell
Failed to initialize CoreCLR, HRESULT: 0x80131500
```

## <a name="Usage_Issues"></a>Usage Issues:

### Unknown glyph fills up prompt:
If you encounter the display below, it is a Windows 10 issue that can pop up on the command prompt or powershell prompt.
The current workaround for this issue is to change the font of the prompt to Consolas.
![alt text](https://github.com/dbcli/mssql-cli/blob/master/screenshots/mssql-cli-display-issue.png "mssql-cli display issue")


## <a name="Reporting_Issues"></a>Reporting Issues:
If the issue you are encountering is not listed above nor filed on our github, please file a issue here [issues](#https://github.com/dbcli/mssql-cli/issues) with the following information listed below and any other additional symptoms of your issue.

* Command used to install mssql-cli
* Python version and location
```
    $ python -V 
    $ where python 
```
* Pip Version and location
```
    $ pip -V
    $ where pip
```
* OS Distribution and version
* Target Server and Database version and edition
* Python environment variables set
