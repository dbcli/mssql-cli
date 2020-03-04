# Publishing to Packages.Microsoft
> Publishing to the Microsoft Repo may only be completed on corp-net. Support for non-corp-net access is not available at the time of this writing. Repo CLI docs may be accessed [here](http://csd-linux-publishing-service.azurewebsites.net/).

## Requirements
1. Install Docker Desktop

## Creating Config File for Publishing
A config file must be created to publish to packages.microsoft repository:
1. On the [Repo Cli](http://csd-linux-publishing-service.azurewebsites.net/client#commands) website, select the **Configure the Repo CLI** tab

## Create the cert

## Build Docker Container
Complete the below command below to create a Docker container with dependencies installed for publishing.

From the root repo directory, run:
```sh
docker build -t mssqlcli-publish-msftrepo -f release_scripts/Packages.Microsoft/Dockerfile . --no-cache
```

## Run Docker Container
This will run the Docker container built using the previous command:
```sh
docker run -it mssqlcli-publish-msftrepo bash
```

## Install Repo CLI
In your Docker container, complete the command below to install the Repo CLI, the tool used to publish packages to Packages.Microsoft.

```sh
apt-get -y install azure-repoapi-client
```

## Publish to Packages.Microsoft Using Repo CLI

### Repo CLI Commands

#### List Uploaded Packages
```sh
repoclient package list | jq '.[] | select(.name=="mssql-cli")'
```
