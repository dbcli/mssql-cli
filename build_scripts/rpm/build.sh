#!/usr/bin/env bash

if [ -z "$1" ]
  then
    echo "Argument should be path to local repo."
    exit 1
fi

export REPO_PATH=$1

rpmbuild -v -bb --clean mssql-cli.spec