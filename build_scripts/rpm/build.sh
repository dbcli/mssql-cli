#!/usr/bin/env bash

if [ -z "$1" ]
  then
    echo "Argument should be path to local repo."
    exit 1
fi

export REPO_PATH=$1

sudo yum repolist
sudo yum update
sudo yum install -y gcc git rpm-build rpm-devel rpmlint make bash diffutils patch rpmdevtools python3 libffi-devel python3-devel openssl-devel

# Clean output dir.
rm -rf ~/rpmbuild
rm -rf ${REPO_PATH}/../rpm_output

# the ',,' makes environment variable lower case in Bash 4+
# needed before switch statement checks for 'true'
MSSQL_CLI_OFFICIAL_BUILD="${MSSQL_CLI_OFFICIAL_BUILD,,}"

# Build rpm package
rpmbuild -v -bb --clean ${REPO_PATH}/build_scripts/rpm/mssql-cli.spec

# Copy build artifact to output dir.
mkdir ${REPO_PATH}/../rpm_output
cp ~/rpmbuild/RPMS/x86_64/*.rpm ${REPO_PATH}/../rpm_output
echo "The archive has also been outputted to ${REPO_PATH}/../rpm_output"
