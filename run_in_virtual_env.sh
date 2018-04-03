#!/bin/bash
# Install virtual env if it doesn't exist.
pip install virtualenv

virtualenv env
source env/bin/activate
$@
deactivate
