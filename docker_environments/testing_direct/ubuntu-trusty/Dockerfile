FROM ubuntu:14.04

ARG MSSQL_CLI_SERVER
ARG MSSQL_CLI_DATABASE
ARG MSSQL_CLI_USER
ARG MSSQL_CLI_PASSWORD
ARG MSSQL_CLI_PKG_DEB

ENV MSSQL_CLI_SERVER=$MSSQL_CLI_SERVER
ENV MSSQL_CLI_DATABASE=$MSSQL_CLI_DATABASE
ENV MSSQL_CLI_USER=$MSSQL_CLI_USER
ENV MSSQL_CLI_PASSWORD=$MSSQL_CLI_PASSWORD

RUN apt-get update
RUN apt-get -y install wget sudo curl
RUN apt-get -y install software-properties-common
RUN apt-get -y install apt-transport-https

# Installs deb from arg
RUN wget $MSSQL_CLI_PKG_DEB
RUN dpkg -i ./mssql-cli_*.deb; exit 0

# Installs missing requirements
RUN apt-get install -y -f
