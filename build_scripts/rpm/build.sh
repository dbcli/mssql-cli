#!/usr/bin/env bash

if [ -z "$1" ]
  then
    echo "Argument should be path to local repo."
    exit 1
fi

local_repo=$1

export REPO_PATH=$local_repo

rpmbuild -v -bb --clean mssql-cli.spec
