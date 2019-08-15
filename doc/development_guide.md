
Development Guide
=================

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

## Table of Contents
1. [Environment Setup](#Environment_Setup)
	1. [Install Python / Clone Source Code](#Install_Python_Clone_Source_Code)
	2. [Create Virtual Environment](#Create_Virtual_Environment)
	3. [Build mssql-cli](#Build_mssql_cli)
	4. [Run mssql-cli From Code](#Run_mssql-cli_From_Code)
	5. [Run Unit Tests / Integration Tests](#Run_Unit_Tests_Integration_Tests)
2. [IDE Setup](#IDE_Setup)
	1. [Install Visual Studio Code](#Install_Visual_Studio_Code)
	2. [Configure Python Settings in Visual Studio Code](#Configure_Python_Settings_in_Visual_Studio_Code)
	3. [How to run mssql-cli with debugger](#How_to_run_mssql_cli_with_debugger)
	4. [How to run unit tests with / without debugger](#How_to_run_unit_tests_with_without_debugger)


# <a name="Environment_Setup"></a>Environment Setup

mssql-cli sources are located on GitHub (https://github.com/dbcli/mssql-cli). In order to contribute to the project, you are expected to: 
-	Have a GitHub account. For Microsoft contributors, follow the guidelines on https://opensourcehub.microsoft.com/ to create, configure and link your account
-	Fork the https://github.com/dbcli/mssql-cli repository into your private GitHub account
-	Create pull requests against the https://github.com/dbcli/mssql-cli repository to get your code changes merged into the project repository.

## <a name="Install_Python_Clone_Source_Code"></a>1. Install Python / Clone Source Code
1.	Install latest Python from http://python.org. Please note that the version of Python that comes preinstalled on OSX is 2.7. It is recommended to install both Python 2.7 and Python3.7 to ensure backwards compatibility for testing.
    #### Windows
    - The latest Python installation package can be downloaded from [here](https://www.python.org/downloads/).  
    - During installation, select the 'Add Python to PATH' option.  Python must be in the PATH environment variable.
    
2. Clone the repo from [https://github.com/dbcli/mssql-cli](https://github.com/dbcli/mssql-cli)

## <a name="Create_Virtual_Environment"></a>2. Create Virtual Environment
When developing on a Python project, it is recommended to do so in a virtual environment. A virtual environment is a sandbox that maintains a copy of all libraries necessary to run python in a isolated environment without interfering with the system or global python. For more information on virtual environments, go to [Virtual Environment Info](virtual_environment_info.md).

If not developing in a virtual environment, please proceed to [Install All Dependencies](#Install_All_Dependencies) 

### 1. Create a virtual environment
Create a virtual environment in a subdirectory of your `<workspaceFolder>` (`<workspaceFolder>/env`, for example). Open command prompt or bash.

##### Windows (Python3.x)
```
set PYLOC=<python3_location>
set PATH=%PYLOC%\Scripts;%PYLOC%;%PATH%
python -m venv <workspaceFolder>\env
```
##### Windows (Python2.x)
```
set PYLOC=<python2_location>
set PATH=%PYLOC%\Scripts;%PYLOC%;%PATH%
python -m pip install --upgrade pip
python -m pip install --upgrade virtualenv
python -m virtualenv <workspaceFolder>\env
```
##### MacOS (Python3.x)
```
python3 -m venv <workspaceFolder>/env
```
##### MacOS (Python2.x)
```
python -m venv <workspaceFolder>/env
```
##### Linux (Python3.x) -- Ubuntu for example
```
sudo apt-get update
sudo apt-get install python3-pip
sudo apt-get install python3-venv
python3 -m venv <workspaceFolder>/env
```
##### Linux (Python2.x) -- Ubuntu for example
```
sudo apt-get update
sudo apt-get install python-pip
python -m pip install --upgrade pip
python -m pip install virtualenv
python -m virtualenv <workspaceFolder>/env
```
    
### 2. Activate Virtual Environment
##### Windows
```
<workspaceFolder>\env\scripts\activate.bat
```
##### MacOS/Linux
```
. <workspaceFolder>/env/bin/activate
```

### (To deactivate the Virtual Environment)
##### Windows/MacOS/Linux
```
deactivate
```

## <a name="Build_mssql_cli"></a>3. Build mssql-cli
General development steps that apply to both a virtual environment or a global environment.
*If working in a virtual environment, do ensure the virtual environment is activated as the first command line of each following script.*

##### Windows
```
<workspaceFolder>\env\scripts\activate.bat

cd <workspaceFolder>
python -m pip install --upgrade pip
python build.py build

set PYTHONPATH=D:\Projects\mssql-cli;%PYTHONPATH%
python dev_setup.py
```
##### MacOS/Linux (Python3.x)
```
. <workspaceFolder>/env/bin/activate

cd <workspaceFolder>
python3 -m pip install --upgrade pip
python3 build.py build

export PYTHONPATH=<workspaceFolder>:${PYTHONPATH}
python3 dev_setup.py
```
##### MacOS/Linux (Python2.x)
```
. <workspaceFolder>/env/bin/activate

cd <workspaceFolder>
python -m pip install --upgrade pip
python build.py build

export PYTHONPATH=<workspaceFolder>:${PYTHONPATH}
python dev_setup.py
```

## <a name="Run_mssql-cli_from_code"></a>4. Run mssql-cli From Code

##### Windows
```
<workspaceFolder>\env\scripts\activate.bat

cd <workspaceFolder>
mssql-cli -S <hostname> -d <database> -U <username>
```
##### MacOS/Linux
```
. <workspaceFolder>/env/bin/activate

cd <workspaceFolder>
. mssql-cli -S <hostname> -d <database> -U <username>
```


## <a name="Run_unit_tests_integration_tests"></a>5. Run Unit Tests / Integration Tests

##### Windows
```
<workspaceFolder>\env\scripts\activate.bat

set MSSQL_CLI_SERVER=<hostname>
set MSSQL_CLI_DATABASE=<database>
set MSSQL_CLI_USER=<username>
set MSSQL_CLI_PASSWORD=<password>

cd <workspaceFolder>
python build.py unit_test
python build.py integration_test
```
##### MacOS/Linux (Python3.x)
```
. <workspaceFolder>/env/bin/activate

export MSSQL_CLI_SERVER=<hostname>
export MSSQL_CLI_DATABASE=<database>
export MSSQL_CLI_USER=<username>
export MSSQL_CLI_PASSWORD=<password>

cd <workspaceFolder>
python3 build.py unit_test
python3 build.py integration_test
```
##### MacOS/Linux (Python2.x)
```
. <workspaceFolder>/env/bin/activate

export MSSQL_CLI_SERVER=<hostname>
export MSSQL_CLI_DATABASE=<database>
export MSSQL_CLI_USER=<username>
export MSSQL_CLI_PASSWORD=<password>

cd <workspaceFolder>
python build.py unit_test
python build.py integration_test
```


# <a name="IDE_Setup"></a>IDE Setup
## <a name="Install_Visual_Studio_Code"></a> 1. Install Visual Studio Code
1.	Install Visual Studio Code
2.	Install the the VS Code [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python)

## 2. <a name="Configure_Python_Settings_in_Visual_Studio_Code"></a> Configure Python Settings in Visual Studio Code
### 1. Activate VSCode Python Extension
Open the workspace folder with VS Code. The python extension is not active yet as in the screenshot.

![image](https://user-images.githubusercontent.com/19577035/63064795-f928bd00-beb7-11e9-8d53-64840a7a8dcb.png)

In order to activate the python extension, select one of the `*.py` file in the explorer on the left.
You will see the extension becomes active and showes current version of python hooked up to the extension by default.

![image](https://user-images.githubusercontent.com/19577035/63064822-1eb5c680-beb8-11e9-8f22-0d3ddad25a95.png)

### 2. Configure .vscode/setting.json
If `<workspaceFolder>/.vscode` does not exists, change one of the user settings to create it. One of the easist way is simply chaning the current version of python to any version.

![image](https://user-images.githubusercontent.com/19577035/63064397-b9f96c80-beb5-11e9-8514-b0e58e83f3a5.png)

And you will see `<workspaceFolder>/.vscode` and `<workspaceFolder>/.vscode/settings.json` file are created.

![image](https://user-images.githubusercontent.com/19577035/63064590-bca89180-beb6-11e9-8800-1bcde427cef0.png)

Update the `<workspaceFolder>/.vscode/settings.json` as shown below:
##### Windows
```
{
    "python.pythonPath": "${workspaceFolder}/env/Scripts/python.exe",
    "python.linting.pylintEnabled": true,
    "python.envFile": "${workspaceFolder}/environments.env",
    "python.testing.nosetestsEnabled": true,
    "python.testing.nosetestArgs": [
        "tests",
        "mssqlcli/jsonrpc/tests",
        "mssqlcli/jsonrpc/contracts/tests"
    ],
    "python.testing.pytestEnabled": false,
    "python.testing.unittestEnabled": false
}
```
##### MacOS / Linux
```
{
    "python.pythonPath": "${workspaceFolder}/env/bin/python",
    "python.linting.pylintEnabled": true,
    "python.envFile": "${workspaceFolder}/environments.env",
    "python.testing.nosetestsEnabled": true,
    "python.testing.nosetestArgs": [
        "tests",
        "mssqlcli/jsonrpc/tests",
        "mssqlcli/jsonrpc/contracts/tests"
    ],
    "python.testing.pytestEnabled": false,
    "python.testing.unittestEnabled": false
}
```

Press `Yes` if any notification comes up for missing dependencies. You should not have got this notification though if you completed [Build mssql-cli](#Build_mssql_cli) step.

![image](https://user-images.githubusercontent.com/19577035/63066150-9b976f00-bebd-11e9-8e31-a786e2eb61f5.png)



### 2. Create environments.env file
Create a file named `<workspaceFolder>/environments.env` with contents:
```
MSSQL_CLI_SERVER=<hostname>
MSSQL_CLI_DATABASE=<database>
MSSQL_CLI_USER=<username>
MSSQL_CLI_PASSWORD=<password>
```

![image](https://user-images.githubusercontent.com/19577035/63066435-e82f7a00-bebe-11e9-9ef0-4b1f78a8e38b.png)


## <a name="How_to_run_mssql_cli_with_debugger"></a> 3. How to run mssql-cli with debugger
### 1. Configure .vscode/launch.json
Go to debug window by clicking debug icon on the left.
If you have no configuration, click the gear icon with red circle badge to create `<workspaceFolder>/.vscode/launch.json` file.

![image](https://user-images.githubusercontent.com/19577035/63065387-b61c1900-beba-11e9-8cb4-2994602ce8ea.png)

Select `Python` for environment.

![image](https://user-images.githubusercontent.com/19577035/63065581-70138500-bebb-11e9-9422-2f24f2bca467.png)

Select `Python File` for debug configuration.

![image](https://user-images.githubusercontent.com/19577035/63065617-99ccac00-bebb-11e9-8f2a-ba1f745551d3.png)

Update the `<workspaceFolder>/.vscode/launch.json` as shown below:
```
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Launch mssql-cli",
            "type": "python",
            "request": "launch",
            "program": "${workspaceRoot}/mssqlcli/main.py",
            "args": [
                "-S", "<hostname>",
                "-d", "<database>",
                "-U", "<username>"
            ],
            "env": {
                "PYTHONPATH":"${workspaceRoot};${env:PYTHONPATH}"
            },
            "console": "integratedTerminal",
        }
    ]
}
```

Here is how it will look like.
![image](https://user-images.githubusercontent.com/19577035/63065683-e1533800-bebb-11e9-9cb6-5513a3ec8650.png)


### 2. Launch mssql-cli debugger
Select `Python: Launch mssql-cli` and hit the green arrow in order to launch mssql-cli debugger.
![image](https://user-images.githubusercontent.com/19577035/63066602-c97db300-bebf-11e9-83ce-f2bfe30c49c1.png)
Debugger runs successfully.
![image](https://user-images.githubusercontent.com/19577035/63066946-87ee0780-bec1-11e9-9b3b-2897d15a651b.png)


## <a name="How_to_run_unit_tests_with_without_debugger"></a> 4. How to run unit tests with / without debugger
### 1. Discover all tests in VSCode
Click `Run Tests` on the bottom of VSCode, and select `Discover Test` among the test menu.
![image](https://user-images.githubusercontent.com/19577035/63067638-c0dbab80-bec4-11e9-8f49-2d407f929813.png)

You can see all the discovered tests after discover process finishes. A test or a group of tests can be executed by one-click in VSCode as shown below.
![image](https://user-images.githubusercontent.com/19577035/63067720-2039bb80-bec5-11e9-8007-f44a8796aa3b.png)

### 2. Run unit test with debugger
Clicking `Debug Test` will start debugger for the unit test as shown below
![image](https://user-images.githubusercontent.com/19577035/63067893-f59c3280-bec5-11e9-8874-6e22821fb608.png)
