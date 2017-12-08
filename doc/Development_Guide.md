Development Guide
=================

## Table of Contents
1. [Preparing your machine](#Preparing_machine)
1. [Environment Setup](#Environment_Setup)
2. [Configuring IDE](#Configure_IDE)
3. [Running Tests](#Running_Tests)
5. [Running mssql-cli](#Run_mssql-cli)


mssql-cli sources are located on GitHub (https://github.com/dbcli/mssql-cli). In order to contribute to the project, you are expected to: 
-	Have a GitHub account. For Microsoft contributors, follow the guidelines on https://opensourcehub.microsoft.com/ to create, configure and link your account
-	Fork the https://github.com/dbcli/mssql-cli repository into your private GitHub account
-	Create pull requests against the https://github.com/dbcli/mssql-cli repository to get your code changes merged into the project repository.

## <a name="Preparing_Machine"></a>1. Preparing your machine
1.	Install latest Python from http://python.org. Please note that the version of Python that comes preinstalled on OSX is 2.7. It is recommended to install both Python 2.7 and Python3.6 to ensure backwards compatibility for testing.
    #### Windows
    - The latest Python installation package can be downloaded from [here](https://www.python.org/downloads/).  
    - During installation, select the 'Add Python to PATH' option.  Python must be in the PATH environment variable.
    
2. Clone the repo from [https://github.com/dbcli/mssql-cli](https://github.com/Microsoft/mssql-cli)

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
    python <clone_root>/dev_setup.py
    ```
## <a name="Configure_IDE"></a>3. Configuring your IDE

#### Visual Studio Code (Any platform)

1.	Install VS Code
2.	Install the the VS Code [Python extension](https://marketplace.visualstudio.com/items?itemName=donjayamanne.python)

The repo has a launch.json file that will launch the version of Python that is first on your path. 

## <a name="Running_Tests"></a>4. Running Tests
Provided your PYTHONPATH was set correctly, you can run the tests from your `<clone_root>` directory.

1. Run unit tests:
    
    **Note**: You must first set the target server and database information connection info via environment variables:
    ##### Windows
    ```
        set MSSQL_CLI_HOST=<Target server name>
        set MSSQL_CLI_DATABASE=<Target database name>
        set MSSQL_CLI_USER=<User name>
        set MSSQL_CLI_PASSWORD=<password>
    ```
    
    ##### MacOSX/Linux (bash)
    ```
        export MSSQL_CLI_HOST=<Target server name>
        export MSSQL_CLI_DATABASE=<Target database name>
        export MSSQL_CLI_USER=<User name>
        export MSSQL_CLI_PASSWORD=<password>
    ```

    Execute the unit tests.
    ```
    python build.py unit_test
    ```
    
2. Run integration tests (code format, unit tests, packaging, integration,) with tox:

    ```
    python build.by integration_test
    ```

## <a name="Run_mssql-cli"></a>5. Running mssql-cli
#### Command line

1.  Invoke mssql-cli using:

    ##### MacOS/Linux (bash):
    ```
    mssql-cli --help
    ```

    ##### Windows:
    ```
    <clone_root>\mssql-cli.bat --help
    ```
    which is equivalent to the following:
    ```
    python -m mssql-cli --help
    ```
