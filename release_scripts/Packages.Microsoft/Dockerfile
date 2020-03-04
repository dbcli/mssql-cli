FROM amd64/ubuntu:18.04 AS builder

RUN apt-get update
RUN apt-get -y install wget curl sudo gnupg gnupg2 gnupg1 jq
RUN apt-get -y install software-properties-common
RUN apt-get -y install apt-transport-https

# Requirements for installing the Repo CLI for Packages.Microsoft
ADD ./release_scripts/Packages.Microsoft/config.json /root/.repoclient/config.json
ADD ./release_scripts/Packages.Microsoft/private.pem /root/private.pem

# Install Repo CLI requirements
RUN curl http://tux-devrepo.corp.microsoft.com/keys/tux-devrepo.asc > tux-devrepo.asc | apt-key add tux-devrepo.asc
RUN echo "deb [arch=amd64] http://tux-devrepo.corp.microsoft.com/repos/tux-dev/ xenial main" | tee /etc/apt/sources.list.d/tuxdev.list
RUN apt-get update

# Add mssql-cli repo
WORKDIR /root
RUN mkdir Repos
RUN mkdir Repos/mssql-cli
ADD . Repos/mssql-cli

# Download latest stable deb and rpm packages
WORKDIR /root
RUN wget https://mssqlcli.blob.core.windows.net/daily/deb/mssql-cli-dev-latest.deb
RUN wget https://mssqlcli.blob.core.windows.net/daily/rpm/mssql-cli-dev-latest.rpm

# add privileges to publish script
WORKDIR /root/Repos/mssql-cli
RUN chmod +x release_scripts/Packages.Microsoft/publish.sh
