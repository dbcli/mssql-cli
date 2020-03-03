# Publishing to Packages.Microsoft
> Publishing to the Microsoft Repo may only be completed on corp-net. Support for non-corp-net access is not available at the time of this writing. Repo CLI docs may be accessed [here](http://csd-linux-publishing-service.azurewebsites.net/).

## Creating Config File for Publishing
A config file must be created to publish to packages.microsoft repository:
1. On the [Repo Cli](http://csd-linux-publishing-service.azurewebsites.net/client#commands) website, select the **Configure the Repo CLI** tab

## Create the cert

## Build Docker Container
Complete the below command below to create a Docker container with dependencies installed for publishing:
```sh
docker build -t mssqlcli-publish-msftrepo .
```

## Run Docker Container

## Install Repo CLI
```sh
apt-get -y install azure-repoapi-client
```

## Commands

### List Uploaded Packages
```sh
repoclient package list | jq '.[] | select(.name=="mssql-cli")'
```
