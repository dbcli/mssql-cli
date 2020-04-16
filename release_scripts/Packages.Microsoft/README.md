# Publishing to Packages.Microsoft
> Please ensure that stable versions of rpm and deb have already been published to daily storage.

> Publishing to the Microsoft Repo may only be completed on corp-net. Support for non-corp-net access is not available at the time of this writing. Repo CLI docs may be accessed [here](http://csd-linux-publishing-service.azurewebsites.net/).

The following steps are required to deploy Linux packages to Packages.Microsoft:
1. Build a Linux environment which supports the Repo CLI installation.
2. Install [Repo CLI](http://csd-linux-publishing-service.azurewebsites.net/client#commands), a tool used to publish to Packages.Microsoft.
3. Publish to each supported Linux distribution.

Much of this process has been automated, however, each step may be conducted manually if desired.

## Creating Linux Environment
A Linux environment needs to be created to install [Repo CLI](http://csd-linux-publishing-service.azurewebsites.net/client#commands), which requires:
1. AMD architecture.
2. Connection to corp-net.
3. Include both config and certificate files, detailed below.

### Required Files for Repo CLI
[Repo CLI](http://csd-linux-publishing-service.azurewebsites.net/client#commands) is the required API to publish Linux packages to Packages.Microsoft. Two files are required to use this tool:
1. **A certificate** used for authenticating with the tool.
2. **A JSON config file** as listed on the [Repo CLI docs](http://csd-linux-publishing-service.azurewebsites.net/client#commands).

#### Certificate
The certificate is hosted on our team's Key Vault account in Azure, under 'Certificates'. Download the certificate as a PEM file and include it in this directory (Packages.Microsoft). Rename the file as **private.pem**.

* If you plan to use the automated publishing process, place **private.pem** in this directory (`<repo root>/release_scripts/Packages.Microsoft/private.pem`).
* If a custom Linux environment is used, the location needs to be in `/root/private.pem`.

#### Config
An incomplete `config.json` file is located in this directory. Complete the empty attributes as follows:
* `"AADClientId"`: points to the mssql-cli app registration, titled **mssql-cli (Registered with Packages.Microsoft)**. The ID can be obtained by accessing the Azure Portal.
* `"AADResource"` and `"AADTenant"`: both point to Packages.Microsoft-specific resources. To obtain these values, access the [Repo CLI](http://csd-linux-publishing-service.azurewebsites.net/client) home page, click the **Configure the Repo CLI** tab, followed by the **Packages.Microsoft** sub-tab.

If you plan to use the automated publishing process, keep this file located as is. Otherwise, copy this file to `/root/.repoclient/config.json` on your Linux machine.

### Create Linux Container
This directory contains a dockerfile that generates a Linux environment that's compliant with Repo CLI.

If a non-Docker Linux environment is desired, you may skip to [Repo CLI Installation](#repo-cli-installation). However, please ensure your Linux machine:
1. Uses AMD architecture
2. Is connected to corp-net

#### Building Docker Container
> Docker Desktop is required and may be installed for macOS or Windows [here](https://www.docker.com/products/docker-desktop).

Complete the below command below to create a Docker container with dependencies installed for publishing.

From the root repo directory, run:
```sh
docker build -t mssqlcli-publish-msftrepo -f release_scripts/Packages.Microsoft/Dockerfile . --no-cache
```

#### Running Docker Container
This will run the Docker container that was built using the previous command.
```sh
docker run -it mssqlcli-publish-msftrepo bash
```

You may now complete the Repo CLI installation, detailed in the next section.

## Repo CLI Installation
[Repo CLI](http://csd-linux-publishing-service.azurewebsites.net/client) is the the tool used to publish packages to Packages.Microsoft. Install the Repo CLI in your Linux environment as follows:

```sh
sudo apt-get -y install azure-repoapi-client
```

Respond to all prompts to complete installation.

## Publishing to Packages.Microsoft Using Repo CLI
The `publish.sh` script will upload deb and rpm packages to Packages.Microsoft by consulting the `supported_repos_prod.json` or `supported_repos_testing.json` file. This data is used to find supported repositories located in Packages.Microsoft.

`publish.sh` takes `'testing'` or `'prod'` parameters as its second argument. Uploading to the testing distribution is effective for testing the installation and usage of mssql-cli on various Linux systems without affecting production.

### Publishing to Testing Channel
From the mssql-cli folder root, make the following command to upload packages to all repositories in the `supported_repos_testing.json` file:
```sh
# use --print to display commands rather than call them
release_scripts/Packages.Microsoft/publish.sh $(pwd) 'testing' --print

# completes call, will publish to Packages.Microsoft
release_scripts/Packages.Microsoft/publish.sh $(pwd) 'testing'
```

Visit the [testing](#testing-distribution-downloads) section for more information on downloading builds from the testing distribution.

### Publishing to Production Channel
When ready for production, change `'testing'` with `'prod'`, which will upload to all repositories in the `supported_repos_prod.json` file:
```sh
# use --print to display commands rather than call them
release_scripts/Packages.Microsoft/publish.sh $(pwd) 'prod' --print

# completes call, will publish to Packages.Microsoft
release_scripts/Packages.Microsoft/publish.sh $(pwd) 'prod'
```

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

# For example:
repoclient repo list | jq '.[] | select(.url=="microsoft-ubuntu-xenial-prod" and .distribution=="testing")'
```
