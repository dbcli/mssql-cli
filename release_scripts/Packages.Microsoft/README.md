# Publishing to Packages.Microsoft
> Publishing to the Microsoft Repo may only be completed on corp-net. Support for non-corp-net access is not available at the time of this writing. Repo CLI docs may be accessed [here](http://csd-linux-publishing-service.azurewebsites.net/).

## Requirements
1. Install Docker Desktop

## Creating Config File for Publishing
A config file must be created to publish to packages.microsoft repository:
1. On the [Repo CLI](http://csd-linux-publishing-service.azurewebsites.net/client#commands) website, select the **Configure the Repo CLI** tab

## Create the Certificate and Config Files
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

#### List Uploaded Packages
```sh
repoclient package list | jq '.[] | select(.name=="mssql-cli")'
```
