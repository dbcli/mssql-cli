mssql-cli release guide
========================================
# Table of Contents
1. [Requirements](#Requirements)
2. [Local builds](#Local)
3. [Daily builds](#Daily)
4. [Official builds](#Official)
 
# <a name="Requirements"></a> Requirements
### Install Dependencies
1.  Add `<clone_root>` to your PYTHONPATH environment variable:
    #### Windows
    ```
    set PYTHONPATH=<clone_root>;%PYTHONPATH%
    ```
    #### OSX/Ubuntu (bash)
    ```
    export PYTHONPATH=<clone_root>:${PYTHONPATH}
    ```
2.	Install the dependencies:
    ```
    python <clone_root>/dev_setup.py
    ```
### Configure Azure Storage Account
1. The Azure Storage account needs a container named **daily**.

2. A sub folder named **mssql-cli** under the previous container.

3. Set the Azure Storage account connection string via environment variable. This will be the storage account where builds get published to.
    #### Windows
    ```
    set AZURE_STORAGE_CONNECTION_STRING=<connection string>
    ```

    #### MacOS/Linux
    ```
    export AZURE_STORAGE_CONNECTION_STRING='<connection_string>'
    ```

# Create Builds
## <a name="Local"></a>Local Builds
The steps below outline how to build mssql-cli locally on your dev environment.
### Build Instructions
1. To build a wheel package for the current platform, run:
    ```
    python build.py build
    ```

### Installation Instructions
2. The prior build step created a wheel package, located in the `./dist/` folder. To test the installation of this wheel package, execute the following from `<clone_root>`, replacing values for `<version>` and `<timestamp>`:
    ```
    sudo pip install --no-index -i ./dist/mssql_cli-<version>.dev<timestamp>-py2.py3-none-win_amd64.whl
    ```
    
## <a name="Daily"></a>Daily Builds
The steps below outline how daily builds of mssql-cli are generated. These steps run on each supported platform via Visual Studio Team Services. 
### Build Instructions
1. Build mssql-cli:
    ```
    python build.py build
    ```

2. Publish build to daily storage account:
    ```
    python release.py publish_daily
    ```
### Installation Instructions
3. Test install from daily storage account:
    ```
    pip install --pre --no-cache --extra-index-url https://mssqlcli.blob.core.windows.net/daily/whl mssql-cli
    ```
    
## <a name="Official"></a>Official Builds
The steps below outline how to build official builds and publish to PYPI.

### <a name="BumpVersion"></a>Bump Version
The versioning format for `mssql-cli` uses the following naming scheme:

	Versioning schema: {major}.{minor}.{patch}
    Example: 1.0.0
To bump a particular segment of the version, from `<clone_root>` execute:
<pre>
> bumpversion major          ->  <b>2</b>.0
> bumpversion minor          ->  1.<b>1</b>
> bumpversion patch          ->  1.0.<b>1</b>

</pre>
Check-in changes after running `bumpversion` and **validating the build output following a version bump**.

**Note**: bumpversion does not allow version bumping if your workspace has pending changes. This is to protect against any manual updates that may have been made which can lead to inconsistent versions across files. If you know what you are doing you can override this by appending `--allow-dirty` to the bumpversion command.

### Publish Build
**Important: ensure that the build is uploaded from macOS.**

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
        password = <Get Password from Azure Key Vault> (https://sqltoolssecretstore.vault.azure.net/secrets/PYPI-AccountName-sqlcli/)

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
    python release.py publish_daily
    ```
    
5. Download official wheels from storage account:
    ```
    python release.py download_official_wheels
    ```
    
6. Publish downloaded wheels to PYPI:
    ```
    python release.py publish_official
    ```
