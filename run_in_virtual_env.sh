#!/bin/bash
virtualenv env
source env/bin/activate
$@
deactivate
