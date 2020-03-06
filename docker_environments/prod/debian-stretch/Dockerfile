FROM debian:9

ARG MSSQL_CLI_SERVER
ARG MSSQL_CLI_DATABASE
ARG MSSQL_CLI_USER
ARG MSSQL_CLI_PASSWORD

ENV MSSQL_CLI_SERVER=$MSSQL_CLI_SERVER
ENV MSSQL_CLI_DATABASE=$MSSQL_CLI_DATABASE
ENV MSSQL_CLI_USER=$MSSQL_CLI_USER
ENV MSSQL_CLI_PASSWORD=$MSSQL_CLI_PASSWORD

# Install system components
RUN apt-get update
RUN apt-get -y install wget curl software-properties-common apt-transport-https gnupg

# Import the public repository GPG keys
RUN wget -qO- https://packages.microsoft.com/keys/microsoft.asc | apt-key add -

# Register the Microsoft Product feed
RUN echo "deb [arch=amd64] https://packages.microsoft.com/debian/9/prod stretch main" | tee /etc/apt/sources.list.d/mssql-cli.list

# Update the list of products
RUN apt-get update

# Install mssql-cli
RUN apt-get install -y mssql-cli

# Installs missing requirements
RUN apt-get install -y -f
