mssql-cli release guide
========================================
## Table of Contents
1. [Requirements](#Requirements)
2. [Version bump](#BumpVersion)
2. [Local builds](#Local)
3. [Daily builds](#Daily)
4. [Official builds](#Official)
 
### <a name="Requirements"></a> Requirements:
1.  Add `<clone_root>` to your PYTHONPATH environment variable:
    ##### Windows
    ```
    set PYTHONPATH=<clone_root>;%PYTHONPATH%
    ```
    ##### OSX/Ubuntu (bash)
    ```
    export PYTHONPATH=<clone_root>:${PYTHONPATH}
    ```
2.	Install the dependencies:
    ```
    python <clone_root>/dev_setup.py
    ```
### Requirements for daily and official builds:
1. A azure storage account with a container named **daily**.

2. A sub folder named **mssql-cli** under the previous container.

3. Set Azure storage account connection string via environment variable, this will be the storage account we are publishing to.
    #### Windows
    ```
       set AZURE_STORAGE_CONNECTION_STRING=<connection string>
    ```
    
    #### MacOS/Linux
    ```
        export AZURE_STORAGE_CONNECTION_STRING='<connection_string>'
    ```

## <a name="BumpVersion"></a>Bump Version

	Versioning schema: {major}.{minor}.{patch}
    Example: 1.0.0
To bump a particular segment of the version, from `<clone_root>` execute:
<pre>
bumpversion major              ->  <b>2</b>.0
bumpversion minor              ->  1.<b>1</b>
bumpversion patch              ->  1.0.<b>1</b>

</pre>

**Note**: bumpversion does not allow version bumping if your workspace has pending changes.This is to protect against any manual updates that may have been made which can lead to inconsistent versions across files. If you know what you are doing you can override this by appending `--allow-dirty` to the bumpversion command.

# <a name="Local"></a>Local builds
The steps below outline how to build mssql-cli locally on your dev environment.
## 1. Build
1. Build mssql-cli wheel for the current platform:
    ```
    Python build.by build
    ```

## 2. Install
1. Test install locally:

	To install the local mssql-scripter wheel package, from `<clone_root>` execute:
    ```
    sudo pip install --no-index -i ./dist/mssql_scripter-1.0.0a1-py2.py3-none-win32.whl
    ```
    
# <a name="Daily"></a>Daily builds
The steps below outline how daily builds of mssql-cli are generated. These steps are ran on each supported platform via Visual Studio Team Services. 
## 1. Build
1. Build mssql-cli:
    ```
    python build.py build
    ```

2. Publish build to daily storage account:
    ```
    python build.py publish_daily
    ```
## 2. Install
3. Test install from daily storage account:
    ```
        pip install --pre --no-cache --extra-index-url https://mssqlcli.blob.core.windows.net/daily mssql-cli
    ```
    
# <a name="Official"></a>Official builds
The steps below outline how to build official builds and publish to PYPI.
## 1. Create a .pypirc configuration file
1. Add a .pypirc configuration file:

    - Create a .pypirc file in your user directory:
        #### Windows: 
            Example: C:\Users\bob\.pypirc
		#### MacOS/Linux: 
            Example: /Users/bob/.pypirc
    
    - Add the following content to the .pypirc file, replace `your_username` and `your_passsword` with your account information created from step 1:
        ```
        [distutils]
        index-servers=
            pypi
        
        [pypi]
        username = sqlcli
        password = <Get Password from Azure Key Vault>

        ```
2. Set env var to indicate a official build:
    #### Windows
    ```
       set MSSQL_CLI_OFFICIAL_BUILD=True
    ```
    
    #### MacOS/Linux
    ```
        export MSSQL_CLI_OFFICIAL_BUILD=True
    ```
3. Build for the current platform:
    ```
        python build.py build
    ```

4. Publish to daily storage account:
    ```
        python build.py publish_daily
    ```
    
5. Download official wheels from storage account:
    ```
        python release.py download_official_wheels
    ```
    
6. Publish downloaded wheels to PYPI:
    ```
        python release.py publish_official
    ```


