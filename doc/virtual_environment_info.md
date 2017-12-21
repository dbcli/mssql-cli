Virtual Environment
========================================

## What is a virtual environment?
    - A isolated Python environment that is installed into a directory.
    - Maintains it's own copy of Python and pip (Python's package manager).
    - When activated all Python operations will route to the Python interpreter within the virtual environment.

## What are the benefits?
    - Keeps your global site-packages directory clean and manageable.
    - Keeps system or user installed Python and it's libraries untouched.
    - Solves the problem of “Project X depends on version 1.x but, Project Y needs 4.x”.
    - Development will not interfere with the System or the user's python. 
    - All libraries installed in the virtual environment will only be used within that environment.

## How to install?

    $ pip install virtualenv

## How to create a virtual environment?
In current directory:
    
    python -m venv .

In a subdirectory that does not exist:

    python -m venv ./new_dir

## How to activate a virtual environment?
##### Windows
```
new_dir\scripts\activate.bat
```
##### MacOS/Linux (bash)
```
. new_dir/bin/activate
```
## How to deactivate a virtual environment?
##### Windows
```
<clone_root>\env\scripts\deactivate.bat
```
##### MacOS/Linux (bash)
```
deactivate
```
