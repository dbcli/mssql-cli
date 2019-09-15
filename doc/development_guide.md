  
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
	4. [Run mssql-cli From Source Code](#Run_mssql-cli_From_Source_Code)
	5. [Run Unit Tests / Integration Tests](#Run_Unit_Tests_Integration_Tests)
2. [IDE Setup](#IDE_Setup)
	1. [Install Visual Studio Code](#Install_Visual_Studio_Code)
	2. [Configure Python Settings in Visual Studio Code](#Configure_Python_Settings_in_Visual_Studio_Code)
	3. [How To Run mssql-cli With Debugger](#How_To_Run_mssql_cli_With_Debugger)
	4. [How To Run Unit Tests With / Without Debugger](#How_To_Run_Unit_Tests_With_Without_Debugger)


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

### 1. Create Virtual Environment
Create a virtual environment in a subdirectory of your `<workspaceRoot>` (`<workspaceRoot>/env`, for example). Open command prompt or bash.

##### Windows (Python3.x)
```
set PYLOC=<python3_location>
set PATH=%PYLOC%\Scripts;%PYLOC%;%PATH%
python -m venv <workspaceRoot>\env
```
##### Windows (Python2.x)
```
set PYLOC=<python2_location>
set PATH=%PYLOC%\Scripts;%PYLOC%;%PATH%
python -m pip install --upgrade pip
python -m pip install --upgrade virtualenv
python -m virtualenv <workspaceRoot>\env
```
##### MacOS (Python3.x)
```
python3 -m venv <workspaceRoot>/env
```
##### MacOS (Python2.x)
```
python -m venv <workspaceRoot>/env
```
##### Linux (Python3.x) -- Ubuntu for example
```
sudo apt-get update
sudo apt-get install python3-pip
sudo apt-get install python3-venv
python3 -m venv <workspaceRoot>/env
```
##### Linux (Python2.x) -- Ubuntu for example
```
sudo apt-get update
sudo apt-get install python-pip
python -m pip install --upgrade pip
python -m pip install virtualenv
python -m virtualenv <workspaceRoot>/env
```
    
### 2. Activate Virtual Environment
##### Windows
```
<workspaceRoot>\env\scripts\activate.bat
```
##### MacOS/Linux
```
. <workspaceRoot>/env/bin/activate
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
<workspaceRoot>\env\scripts\activate.bat

cd <workspaceRoot>
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python build.py build
```
##### MacOS/Linux (Python3.x)
```
. <workspaceRoot>/env/bin/activate

cd <workspaceRoot>
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements-dev.txt
python3 build.py build
```
##### MacOS/Linux (Python2.x)
```
. <workspaceRoot>/env/bin/activate

cd <workspaceRoot>
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python build.py build
```

## <a name="Run_mssql-cli_From_Source_Code"></a>4. Run mssql-cli From Source Code

##### Windows
```
<workspaceRoot>\env\scripts\activate.bat

cd <workspaceRoot>
mssql-cli -S <hostname> -d <database> -U <username>
```
##### MacOS/Linux
```
. <workspaceRoot>/env/bin/activate

cd <workspaceRoot>
. mssql-cli -S <hostname> -d <database> -U <username>
```


## <a name="Run_unit_tests_integration_tests"></a>5. Run Unit Tests / Integration Tests

##### Windows
```
<workspaceRoot>\env\scripts\activate.bat

set MSSQL_CLI_SERVER=<hostname>
set MSSQL_CLI_DATABASE=<database>
set MSSQL_CLI_USER=<username>
set MSSQL_CLI_PASSWORD=<password>

cd <workspaceRoot>
python build.py unit_test
python build.py integration_test
```
##### MacOS/Linux (Python3.x)
```
. <workspaceRoot>/env/bin/activate

export MSSQL_CLI_SERVER=<hostname>
export MSSQL_CLI_DATABASE=<database>
export MSSQL_CLI_USER=<username>
export MSSQL_CLI_PASSWORD=<password>

cd <workspaceRoot>
python3 build.py unit_test
python3 build.py integration_test
```
##### MacOS/Linux (Python2.x)
```
. <workspaceRoot>/env/bin/activate

export MSSQL_CLI_SERVER=<hostname>
export MSSQL_CLI_DATABASE=<database>
export MSSQL_CLI_USER=<username>
export MSSQL_CLI_PASSWORD=<password>

cd <workspaceRoot>
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



### 2. Create .env file
Create a file named `<workspaceRoot>/.env` with contents:
```
MSSQL_CLI_SERVER=<hostname>
MSSQL_CLI_DATABASE=<database>
MSSQL_CLI_USER=<username>
MSSQL_CLI_PASSWORD=<password>
```


## <a name="How_To_Run_mssql_cli_With_Debugger"></a> 3. How To Run mssql_cli With Debugger

Select `Python: Launch mssql-cli` and click the green arrow in order to launch mssql-cli debugger.
![image](https://user-images.githubusercontent.com/19577035/63066602-c97db300-bebf-11e9-83ce-f2bfe30c49c1.png)
Debugger will run successfully as shown below.
![image](https://user-images.githubusercontent.com/19577035/63066946-87ee0780-bec1-11e9-9b3b-2897d15a651b.png)


## <a name="How_To_Run_Unit_Tests_With_Without_Debugger"></a> 4. How To Run Unit Tests With / Without Debugger
### 1. Discover All Unit Tests Of Project In VSCode
Click `Run Tests` on the bottom of VSCode, and select `Discover Tests` among the test menu.
![image](https://user-images.githubusercontent.com/19577035/63067638-c0dbab80-bec4-11e9-8f49-2d407f929813.png)

You can see all the discovered unit tests after discover process finishes. A test or a group of tests can be executed by one-click in VSCode as shown below.
![image](https://user-images.githubusercontent.com/19577035/63067720-2039bb80-bec5-11e9-8007-f44a8796aa3b.png)

### 2. Run Unit Test In VSCode
Run unit tests as shown below.
![image](https://user-images.githubusercontent.com/19577035/63145132-ffe42c80-bfaa-11e9-9afe-c7fbf5424930.png)


### 3. Run Unit Test With Debugger
Clicking `Debug Test` will start debugger for a corresponding unit test as shown below.
![image](https://user-images.githubusercontent.com/19577035/63067893-f59c3280-bec5-11e9-8874-6e22821fb608.png)
