Development Guide
=================

## Table of Contents
1. [Preparing your machine](#Preparing_machine)
1. [Environment Setup](#Environment_Setup)
2. [Configuring IDE](#Configure_IDE)
3. [Running Tests](#Running_Tests)
4. [Running mssql-cli](#Run_mssql-cli)
4. [Packaging](pypi_release_steps.md)

See the [Architecture Guide](architecture_guide.md) for details on how mssql-cli is designed and implemented.

mssql-cli sources are located on GitHub (https://github.com/dbcli/mssql-cli). In order to contribute to the project, you are expected to: 
-	Have a GitHub account. For Microsoft contributors, follow the guidelines on https://opensourcehub.microsoft.com/ to create, configure and link your account
-	Fork the  https://github.com/dbcli/mssql-cli repository into your private GitHub account
-	Create pull requests against the https://github.com/dbcli/mssql-cli repository to get your code changes merged into the project repository.

## <a name="Preparing_Machine"></a>1. Preparing your machine
1.	Install latest Python from http://python.org. Please note that the version of Python that comes preinstalled on OSX is 2.7. It is recommended to install both Python 2.7 and Python3.6 to ensure backwards compatibility for testing.
    #### Windows
    - The latest Python installation package can be downloaded from [here](https://www.python.org/downloads/).  
    - During installation, select the 'Add Python to PATH' option.  Python must be in the PATH environment variable.
    
2. Clone the repo from [https://github.com/dbcli/mssql-cli](https://github.com/dbcli/mssql-cli)

## <a name="Environment_Setup"></a>2. Environment Setup
When developing on a Python project, it is recommended to do so in a virtual environment. A virtual environment is a sandbox that maintains a copy of all libraries necessary to run python in a isolated environment without interfering with the system or global python. For more information on virtual environments, go to [Virtual Environment Info](docs/virtual_environment_info.md).

If not developing in a virtual environment, please proceed to [Development Setup](#Development) 
### Virtual Environment
1. Create a virtual environment in a subdirectory of your `<clone_root>`, using `<clone_root>/env` as a example:
 
     ##### Windows
    ```
    python -m venv <clone_root>\env
    ```
    ##### MacOS/Linux (bash)
    ```
    python –m venv <clone_root>/env
    ```
2.  Activate the env virtual environment by running:

    ##### Windows
    ```
    <clone_root>\env\scripts\activate.bat
    ```
    ##### MacOS/Linux (bash)
    ```
    . <clone_root>/env/bin/activate
    ```
3. To deactivate the virtual environment:

    ##### Windows
    ```
    <clone_root>\env\scripts\deactivate.bat
    ```
    ##### MacOS/Linux (bash)
    ```
    deactivate
    ```
### <a name="Development"></a>Development Setup
General development steps that apply to both a virtual environment or a global environment. If working in a virtual environment, do ensure the virtual environment is activated.
1.  Add `<clone_root>` to your PYTHONPATH environment variable:

    ##### Windows
    ```
    set PYTHONPATH=<clone_root>;%PYTHONPATH%
    ```
    ##### MacOS/Linux (bash)
    ```
    export PYTHONPATH=<clone_root>:${PYTHONPATH}
    ```
2.	Install the dependencies:
    ```
    python <clone_root>/dev_setup.py clean
    ```
## <a name="Configure_IDE"></a>3. Configuring your IDE
#### Visual Studio (Windows only)
1.	Install [Python Tools for Visual Studio](https://github.com/Microsoft/PTVS)
2.	Open the `<clone_root>\mssql-cli.pyproj` project in Visual Studio


#### Visual Studio Code (Any platform)

1.	Install VS Code
2.	Install the the VS Code [Python extension](https://marketplace.visualstudio.com/items?itemName=donjayamanne.python)

The repo has a launch.json file that will launch the version of Python that is first on your path. 

## <a name="Running_Tests"></a>4. Running Tests
Provided your PYTHONPATH was set correctly, you can run the tests from your `<clone_root>` directory.

1. Run end to end tests (code format, unit tests, packaging, integration,) with tox:
    

    ```
    tox
    ```
    **Note**: Tox is used run full suite of tests in each python version. Running the command above will run the full suite of tests against Python 2.7 and Python 3.6, if installed. More info can be found at [tox testing.](http://tox.readthedocs.io/en/latest/index.html)

    Run tox tests against specific Python version:

    ```
    tox -e py27
    tox -e py36
    ```

    **Recommended**: Recreate virtual environment on each run to ensure tests are not executing against cached changes.

    ```
    tox --recreate -e py27
    tox --recreate -e py36
    ```
2. Run unit tests with code coverage only:

    ```
    pytest --cov mssqlcli
    ```
2. Running tests for specific components:
  
    To test the mssqlcli:
    ```
    pytest mssqlcli/tests
    ```
    To test the jsonrpc library:
    ```
    pytest mssqlcli/jsonrpc/tests
    ```

    To test the scripting service:
    ```
    pytest mssqlcli/jsonrpc/contracts/tests
    ```

## <a name="Run_mssql-cli"></a>5. Running mssql-cli
#### Command line

1.  Invoke mssql-cli using:

    ##### MacOS/Linux (bash):
    ```
    mssql-cli -h
    ```

    ##### Windows:
    ```
    <clone_root>\mssql-cli.bat -h
    ```
    which is equivalent to the following:
    ```
    python -m mssqlcli -h
    ```