# mssql-cli on Docker
mssql-cli supports a variety of Docker environments. This article presents information for:
1. Installing mssql-cli in your own Docker container.
2. Automating build and run of multiple Docker containers for easier testing.

## Dockerfile Examples
The [prod](https://github.com/dbcli/mssql-cli/tree/master/docker_environments/prod/) folder contains example Dockerfiles for each supported Linux distribution.

## Testing Docker Environments
mssql-cli provides automated scripts for building and running multiple Docker containers. The automation works by:
1. Running an initial script to build Docker containers for each Dockerfile in a specified folder.
2. Running a secondary script to interactively run each built container with mssql-cli pre-installed. Exiting the container will automatically run the next Docker container.

### Requirements for Automated Testing
1. **Docker Desktop.** Install Docker Desktop from the [Docker website](https://www.docker.com/products/docker-desktop).
2. **RedHat registry login.** For SQL Tools team members, please consult the team OneNote for using RHEL company credentials. Call `docker login registry.redhat.io` and log in with your credentials.

### Building Docker Containers for Testing

#### Set Environment Variables
Consult the mssql-cli section under the 'Tooling Master Notebook' OneNote to obtain values for RedHat credentials:

> Note: replace `export` with `set` if using Windows.

```sh
export MSSQL_CLI_PKG_DEB=<direct link to .deb package>
export MSSQL_CLI_PKG_RPM=<direct link to .rpm package>
export REDHAT_USERNAME=<RedHat username>
export REDHAT_PASSWORD=<RedHat password>
```

#### Running Build Script
From the `docker_environments` folder, run:
```sh
# Builds a Docker container for each Dockerfile in a specified folder.
# For example: ./build_containers.sh $(pwd) testing_direct --no-cache
./build_containers.sh $(pwd) <folder-name> --no-cache
```

The `testing_direct` folder should be used for testing builds hosted in the Azure daily storage account.

### Automated Container Runs for Testing
The `run_containers.sh` script will:
1. Interactively run each built container from the `build_containers.sh` script.
2. Allow for mssql-cli testing inside the interactive container.
3. Upon `exit` will interactively run the next pre-built container.

From the `docker_environments` folder, run:
```sh
# Runs each pre-built Docker container specified in a folder.
# For example: ./run_containers.sh $(pwd) testing_direct
./run_containers.sh $(pwd) <folder-name>
```

This will automatically run each built container in an interactive console. Simply call `mssql-cli` to test the installation.

When you're done, exit mssql-cli and type `exit` to move on to the next container.

#### Clearning Space After Testing
Creating multiple Docker containers can take up substantial space on your drive. To clear space, call:
```sh
# WARNING: this command may remove unintended Docker containers, please use with caution.
docker system prune
```
