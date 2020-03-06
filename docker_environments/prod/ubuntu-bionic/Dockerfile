FROM ubuntu:18.04

ARG MSSQL_CLI_SERVER
ARG MSSQL_CLI_DATABASE
ARG MSSQL_CLI_USER
ARG MSSQL_CLI_PASSWORD

ENV MSSQL_CLI_SERVER=$MSSQL_CLI_SERVER
ENV MSSQL_CLI_DATABASE=$MSSQL_CLI_DATABASE
ENV MSSQL_CLI_USER=$MSSQL_CLI_USER
ENV MSSQL_CLI_PASSWORD=$MSSQL_CLI_PASSWORD

RUN apt-get update
RUN apt-get -y install wget curl
RUN apt-get -y install software-properties-common
RUN apt-get -y install apt-transport-https

# Installs mssql-cli from Packages.Microsoft
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -

# Use for pulling from prod channel
RUN apt-add-repository https://packages.microsoft.com/ubuntu/18.04/prod

RUN apt-get update
RUN apt-get install -y mssql-cli

# Installs missing requirements
RUN apt-get install -y -f
