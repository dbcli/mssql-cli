FROM registry.redhat.io/rhel7.0

ARG MSSQL_CLI_SERVER
ARG MSSQL_CLI_DATABASE
ARG MSSQL_CLI_USER
ARG MSSQL_CLI_PASSWORD
ARG REDHAT_USERNAME
ARG REDHAT_PASSWORD

ENV MSSQL_CLI_SERVER=$MSSQL_CLI_SERVER
ENV MSSQL_CLI_DATABASE=$MSSQL_CLI_DATABASE
ENV MSSQL_CLI_USER=$MSSQL_CLI_USER
ENV MSSQL_CLI_PASSWORD=$MSSQL_CLI_PASSWORD

RUN subscription-manager register --username $REDHAT_USERNAME --password $REDHAT_PASSWORD --auto-attach
RUN yum install -y wget libicu libunwind less

RUN rpm -Uvh https://packages.microsoft.com/config/rhel/7/packages-microsoft-prod.rpm
RUN yum install -y mssql-cli
