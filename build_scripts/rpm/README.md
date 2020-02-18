# RPM Packaging

## Building the RPM Package

### Building with Docker
From the root repo directory, run:
```
docker build \
--build-arg AZURE_STORAGE_CONNECTION_STRING=${AZURE_STORAGE_CONNECTION_STRING} \
--build-arg MSSQL_CLI_OFFICIAL_BUILD=${MSSQL_CLI_OFFICIAL_BUILD} \
-t mssqlcli-rpm-build \
-f build_scripts/rpm/Dockerfile . --no-cache
```

### Release RPM Package to Daily Storage with Docker
After the docker container is built, call:
```
docker run mssqlcli-rpm-build python3 release.py publish_daily_rpm
```

### Building without Docker
On a build machine (e.g. new CentOS 7 VM) run the following.

Install dependencies required to build:
Required for rpm build tools & required to build mssql-cli.
```
sudo yum install -y gcc git rpm-build rpm-devel rpmlint make bash coreutils diffutils patch rpmdevtools python libffi-devel python-devel openssl-devel
```

Build example:
Note: use the full path to the repo path, not a relative path.
```
git clone https://github.com/dbcli/mssql-cli
cd mssql-cli
build_scripts/rpm/build.sh $(pwd)
```

## Verification

```
sudo yum install -y libicu
sudo rpm -i /root/rpmbuild/RPMS/x86_64/mssql-cli*.rpm
mssql-cli --version
```

Check the file permissions of the package:  
```
rpmlint /root/rpmbuild/RPMS/x86_64/mssql-cli*.rpm
```

Check the file permissions of the package:  
```
rpm -qlvp /root/rpmbuild/RPMS/x86_64/mssql-cli*.rpm
```

To remove:  
```
sudo rpm -e mssql-cli
```

## Links

https://fedoraproject.org/wiki/How_to_create_an_RPM_package

https://fedoraproject.org/wiki/Packaging:RPMMacros?rd=Packaging/RPMMacros
