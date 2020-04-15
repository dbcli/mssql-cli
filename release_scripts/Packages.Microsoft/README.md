# Publishing to Packages.Microsoft
> Please ensure that stable versions of rpm and deb have already been published to daily storage.

> Publishing to the Microsoft Repo may only be completed on corp-net. Support for non-corp-net access is not available at the time of this writing. Repo CLI docs may be accessed [here](http://csd-linux-publishing-service.azurewebsites.net/).

## Requirements

### Install Docker Desktop
You can install Docker Desktop for macOS and Windows [here](https://www.docker.com/products/docker-desktop).

### Generate Required Files for Repo CLI
[Repo CLI](http://csd-linux-publishing-service.azurewebsites.net/client#commands) is the required API to publish Linux packages to Packages.Microsoft. Two files are required to use this tool:
1. **A certificate** used for authenticating with the tool.
2. **A JSON config file** as listed on the [Repo CLI docs](http://csd-linux-publishing-service.azurewebsites.net/client#commands).

#### Download Certificate
The certificate is hosted on the team's key vault account in Azure, under 'Certificates'. Download the certificate as a PEM file and include it in this directory (Packages.Microsoft). Rename the file as **private.pem**.

#### Download Config
> This section needs to be completed.

## Build Docker Container
Complete the below command below to create a Docker container with dependencies installed for publishing.

From the root repo directory, run:
```sh
docker build -t mssqlcli-publish-msftrepo -f release_scripts/Packages.Microsoft/Dockerfile . --no-cache
```

## Run Docker Container
This will run the Docker container built using the previous command.
```sh
docker run -it mssqlcli-publish-msftrepo bash
```

## Install Repo CLI
In your Docker container, complete the command below to install the Repo CLI, the tool used to publish packages to Packages.Microsoft.

```sh
apt-get -y install azure-repoapi-client
```

## Publish to Packages.Microsoft Using Repo CLI
The `publish.sh` script will upload deb and rpm packages to Packages.Microsoft by consulting the `supported_repos_prod.json` or `supported_repos_testing.json` file. This data is used to find supported repositories located in Packages.Microsoft.

`publish.sh` takes `'testing'` or `'prod'` parameters as its second argument. Uploading to the testing distribution is effective for testing the installation and usage of mssql-cli on various Linux systems without affecting production.

### Publish to Testing
From the mssql-cli folder root, make the following command to upload packages to all repositories in the `supported_repos_testing.json` file:
```sh
release_scripts/Packages.Microsoft/publish.sh $(pwd) 'testing'
```

Visit the [testing](#testing-distribution-downloads) section for more information on downloading builds from the testing distribution.

### Publish to Production
When ready for production, change `'testing'` with `'prod'`, which will upload to all repositories in the `supported_repos_prod.json` file:
```sh
release_scripts/Packages.Microsoft/publish.sh $(pwd) 'prod'
```

## Testing Distribution Downloads
> This section needs to be completed.

## Repo CLI Commands
This list below contains frequently used commands to navigate the Repo CLI API:

#### Upload Single Package
Packages.Microsoft uses **repositories** to distinguish publishing channels. mssql-cli publishes .deb and .rpm packages directly to repositories, which map to a Linux distribution (i.e. Ubuntu 16.04) along with it's distribution channel (i.e. prod or testing). The [list uploaded pacakges](#list-uploaded-packages) command will display a list respositories with previously-published mssql-cli packages.

The call below uploads a .deb or .rpm package to a specificed repository in Packages.Microsoft:
```sh
repoclient package add <package filepath> -r <repo ID>
```

#### List Uploaded Packages
Use the call below to display a history of previously-published mssql-cli packages:
```sh
repoclient package list | jq '.[] | select(.name=="mssql-cli")'
```

#### List Repositories by Linux Version and Distribution Channel
Use the below command to list Packages.Microsoft repository information, with filters for Linux OS and distribution channel:

```sh
repoclient repo list | jq '.[] | select(.url=="<Linux OS name>" and .distribution=="<distribution>")'
```

For example: `repoclient repo list | jq '.[] | select(.url=="microsoft-ubuntu-xenial-prod" and .distribution=="testing")'`
