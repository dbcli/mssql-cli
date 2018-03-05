Debian Packaging
================

Updating the Debian package
---------------------------

On a build machine (e.g. new Ubuntu 14.04 VM), run the build script.

For example:
```
git clone https://github.com/dbcli/mssql-cli
cd mssql-cli
export BUILD_ARTIFACT_DIR=$(mktemp -d)\
  && build_scripts/debian/build.sh $(pwd)
```

Note: The paths above have to be full paths, not relative otherwise the build will fail.

Now you have built the package, upload the package to the apt repository.


Verification
------------

CLI_VERSION can be found in *build_scripts/debian/build.sh*
```
sudo dpkg -i mssql-cli_${CLI_VERSION}-1_all.deb
az
az --version
```
