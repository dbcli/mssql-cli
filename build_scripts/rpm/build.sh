#!/usr/bin/env bash

if [ -z "$1" ]
  then
    echo "Argument should be path to local repo."
    exit 1
fi

export REPO_PATH=$1

# Clean output dir.
rm -rf ~/rpmbuild
rm -rf ${REPO_PATH}/../rpm_output

rpmbuild -v -bb --clean mssql-cli.spec

# Copy build artifact to output dir.
mkdir ${REPO_PATH}/../rpm_output
cp ~/rpmbuild/RPMS/x86_64/*.rpm ${REPO_PATH}/../rpm_output
echo "The archive has also been outputted to ${REPO_PATH}/../rpm_output"
