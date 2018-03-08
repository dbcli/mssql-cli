#!/usr/bin/env bash

CLI_VERSION=0.10.0

set -ex
: "${BUILD_ARTIFACT_DIR:?BUILD_ARTIFACT_DIR environment variable not set.}"

if [ -z "$1" ]
  then
    echo "Argument should be path to local repo."
    exit 1
fi

local_repo=$1

sudo apt-get update

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
debian_directory_creator=$script_dir/dir_creator.sh

# Install dependencies for the build
sudo apt-get install -y libssl-dev libffi-dev debhelper
# Download, Extract, Patch, Build CLI
tmp_pkg_dir=$(mktemp -d)
working_dir=$(mktemp -d)
cd $working_dir
source_dir=$local_repo
deb_file=$local_repo/../mssql-cli_$CLI_VERSION-${CLI_VERSION_REVISION:=1}_all.deb

# clean up old build output
if [ -d "$source_dir/debian" ]
  then
    rm -rf $source_dir/debian
fi

# Freeze mssql-cli
cd $source_dir
python3 build.py freeze;
cd -

# Add the debian files.
mkdir $source_dir/debian
# Create temp dir for the debian/ directory used for CLI build.
cli_debian_dir_tmp=$(mktemp -d)

$debian_directory_creator $cli_debian_dir_tmp $source_dir $CLI_VERSION
cp -r $cli_debian_dir_tmp/* $source_dir/debian
cd $source_dir
dpkg-buildpackage -us -uc
echo "The archive is available at $working_dir/mssql-cli_$CLI_VERSION-${CLI_VERSION_REVISION:=1}_all.deb"
cp $deb_file ${BUILD_ARTIFACT_DIR}
echo "The archive has also been copied to ${BUILD_ARTIFACT_DIR}"
echo "Done."
