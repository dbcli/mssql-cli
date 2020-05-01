# mssql-cli Release Guide

## Table of Contents
1. [Requirements](#requirements)
2. [Creating a New Version](#creating-a-new-version)
3. [Generating Release Files](#generating-release-files)
4. [Publishing Release Files](#publishing-release-files)
5. [Update Links in Installation Readme](#Update-Links-in-Installation-Readme)
6. [Installing Specific Release Files from Azure Storage](#installing-specific-release-files-from-azure-storage)


## Requirements
### Installing Dependencies
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
### Azure Storage Account Configuration
1. The Azure Storage account needs a container named **daily**.

2. A sub folder named **mssql-cli** under the previous container.

3. Set the Azure Storage account connection string via environment variable. This will be the storage account where builds get published to.

    **Windows:**
    ```
    set AZURE_STORAGE_CONNECTION_STRING=<connection string>
    ```

    **MacOS/Linux:**
    ```
    export AZURE_STORAGE_CONNECTION_STRING='<connection_string>'
    ```

## Creating a New Version
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


## Generating Release Files
The steps below outline how to create wheel and source distribution files to publish to Azure Storage, and eventually PyPI for official release.

### Daily Release Configuration
Release files are generated for daily release by default, as long as the `MSSQL_CLI_OFFICIAL_BUILD` environment variable is **not** set to `True`.

### Official Release Configuration
The `MSSQL_CLI_OFFICIAL_BUILD` enviornment variable must be set to `True` before build files are created. Although this step can be completed locally, we recommend running production pipelines in Azure DevOps with the enviornment variable set for each run.

If configured locally, instructions per OS are as follows:
- **Windows**: `set MSSQL_CLI_OFFICIAL_BUILD=True`
- **macOS/Linux**: `export MSSQL_CLI_OFFICIAL_BUILD=True`

### Building Release Files
To build a release package with wheel and source distribution files for the current platform, run:
```
python build.py build
```
Distribution files will be generated in `./dist/`. These files are eventually published to Azure Storage and PyPI for distribution.

**Note:** source distribution files will only get created on macOS. This platform was arbitrarily chosen to prevent redundant copies of source distributions when `build` is run on each platform in Azure DevOps.

## Publishing Release Files
The following instructions outline how to publish release files once generated n the `./dist/` folder.

### Publishing Daily Builds to Azure Storage
Publish build to daily storage account by calling:
```
python release.py publish_daily
```
    
### Publishing Official Builds
The steps below outline how to build official builds and publish to PyPI.

#### Configuration with PyPI
A `.pypirc` configuration file must be created in order to publish to PyPI. Place in the following user directories.

Examples for each OS:
* Windows: `C:\Users\bob\.pypirc`
* MacOS/Linux: `/Users/bob/.pypirc`

Add the below contents to the `.pypirc` file. **Note**: consult the mssql-cli OneNote for obtaining access to Azure Key Vault credentials, needed below.

```
[distutils]
index-servers=
    pypi
    testpypi

[pypi]
username: sqlcli
password: <Get Password from Azure Key Vault>

[testpypi]
repository: https://test.pypi.org/legacy/
username: sqlcli
password: <Get Password from Azure Key Vault>
```

#### Test Publishing with TestPyPI

[TestPyPi](https://test.pypi.org) can be used to test distribution before going to production. To test publishing to TestPyPI, use the above `.pypirc` file and call:
```
twine upload --repository testpypi dist/*
```

[Click here](https://packaging.python.org/guides/using-testpypi/) to view TestPyPI docs.

#### Publishing Official Release Files to PyPI
**Important: ensure that the build is uploaded from macOS.**

Follow the instructions below to publish a new release to PyPI after official release build files have been published to Azure Storage:
    
1. Download official wheels from storage account:
    ```
    python release.py download_official_wheels
    ```
    
2. Publish downloaded wheels to PyPI:
    ```
    python release.py publish_official
    ```

## Update Links in Installation Readme
Once a new official version has been published, please update the links in the [installation readme](https://github.com/dbcli/mssql-cli/tree/master/doc/installation).

## Installing Specific Release Files from Azure Storage
To test the installation a wheel or source distribution, execute the following from `<clone_root>`, replacing values for `<version>` and `<timestamp>`:
```
pip install --no-index -i ./dist/mssql_cli-<version>.dev<timestamp>-py2.py3-none-win_amd64.whl
```


To install the latest release file from the daily storage account, call:
```
pip install --pre --no-cache --extra-index-url https://mssqlcli.blob.core.windows.net/daily/whl mssql-cli
```
