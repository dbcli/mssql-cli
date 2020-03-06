FROM centos:8

ARG MSSQL_CLI_SERVER
ARG MSSQL_CLI_DATABASE
ARG MSSQL_CLI_USER
ARG MSSQL_CLI_PASSWORD

ENV MSSQL_CLI_SERVER=$MSSQL_CLI_SERVER
ENV MSSQL_CLI_DATABASE=$MSSQL_CLI_DATABASE
ENV MSSQL_CLI_USER=$MSSQL_CLI_USER
ENV MSSQL_CLI_PASSWORD=$MSSQL_CLI_PASSWORD

# Installs dependencies
RUN yum update -y
RUN yum install -y epel-release
RUN yum install -y wget libicu libunwind less

# Installs mssql-cli
RUN rpm --import https://packages.microsoft.com/keys/microsoft.asc
RUN curl -o /etc/yum.repos.d/mssql-cli.repo https://packages.microsoft.com/config/centos/8/prod.repo
RUN yum install -y mssql-cli
