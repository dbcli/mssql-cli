# RPM Packaging

## Building the RPM Package

### Building with Docker
From the root repo directory, run:
```sh
docker build \
--build-arg AZURE_STORAGE_CONNECTION_STRING=${AZURE_STORAGE_CONNECTION_STRING} \
--build-arg MSSQL_CLI_OFFICIAL_BUILD=${MSSQL_CLI_OFFICIAL_BUILD} \
-t mssqlcli-rpm-build \
-f build_scripts/rpm/Dockerfile . --no-cache
```

### Release RPM Package to Daily Storage with Docker
> Note: it is recommended to publish packages using Azure DevOps pipelines.

Run the the docker container after it is built:
```sh
docker run -it mssqlcli-rpm-build bash
```

Inside the console, complete the following calls:
```sh
python3 -m pip install -r requirements-dev.txt
python3 release.py publish_daily_rpm
```

### Building without Docker
On a build machine (e.g. new CentOS 7 VM) run the following.

Install dependencies required to build:
Required for rpm build tools & required to build mssql-cli.
```sh
sudo yum install -y gcc git rpm-build rpm-devel rpmlint make bash coreutils diffutils patch rpmdevtools python libffi-devel python-devel openssl-devel
```

Build example:
Note: use the full path to the repo path, not a relative path.
```sh
git clone https://github.com/dbcli/mssql-cli
cd mssql-cli
build_scripts/rpm/build.sh $(pwd)
```

## Verification

```sh
sudo yum install -y epel-release
sudo yum install -y libunwind libicu
sudo rpm -i /root/rpmbuild/RPMS/x86_64/mssql-cli*.rpm
mssql-cli --version
```

Check the file permissions of the package:  
```sh
rpmlint /root/rpmbuild/RPMS/x86_64/mssql-cli*.rpm
```

Check the file permissions of the package:  
```sh
rpm -qlvp /root/rpmbuild/RPMS/x86_64/mssql-cli*.rpm
```

To remove:  
```sh
sudo rpm -e mssql-cli
```

## Links

https://fedoraproject.org/wiki/How_to_create_an_RPM_package

https://fedoraproject.org/wiki/Packaging:RPMMacros?rd=Packaging/RPMMacros
