FROM amd64/ubuntu:18.04 AS builder

RUN apt-get update
RUN apt-get -y install nano wget curl sudo gnupg gnupg2 gnupg1
RUN apt-get -y install software-properties-common
RUN apt-get -y install apt-transport-https

# Requirements for installing the Repo CLI for Packages.Microsoft
ADD ./config.json /root/.repoclient/config.json
ADD ./private.pem /root/private.pem

RUN curl http://tux-devrepo.corp.microsoft.com/keys/tux-devrepo.asc > tux-devrepo.asc | apt-key add tux-devrepo.asc
RUN echo "deb [arch=amd64] http://tux-devrepo.corp.microsoft.com/repos/tux-dev/ xenial main" | tee /etc/apt/sources.list.d/tuxdev.list
RUN apt-get update

# Download latest stable deb and rpm packages
RUN wget https://mssqlcli.blob.core.windows.net/daily/deb/mssql-cli-dev-latest.deb
RUN wget https://mssqlcli.blob.core.windows.net/daily/rpm/mssql-cli-dev-latest.rpm
