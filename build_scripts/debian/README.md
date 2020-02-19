# Debian Packaging

## Build Debian Package

### Build with Docker
From the root repo directory, run:
```
docker build \
--build-arg AZURE_STORAGE_CONNECTION_STRING=${AZURE_STORAGE_CONNECTION_STRING} \
--build-arg MSSQL_CLI_OFFICIAL_BUILD=${MSSQL_CLI_OFFICIAL_BUILD} \
-t mssqlcli-ubuntu16-build \
-f build_scripts/debian/Dockerfile . --no-cache
```

### Release .deb to Daily Storage with Docker
After the docker container is built, call:
```
docker run mssqlcli-ubuntu16-build python3 release.py publish_daily_deb
```

### Build Debian Package without Docker

On a build machine (e.g. new Ubuntu 14.04 VM), run the build script.

For example:
```
git clone https://github.com/dbcli/mssql-cli
cd mssql-cli
build_scripts/debian/build.sh $(pwd)
```

Note: The paths above have to be full paths, not relative otherwise the build will fail.

Now you have built the package, upload the package to the apt repository.


## Verification

CLI_VERSION can be found in *build_scripts/debian/build.sh*
```
sudo dpkg -i mssql-cli_0.10.0.dev-1_all.deb
mssql-cli --version
mssql-cli -h
```
