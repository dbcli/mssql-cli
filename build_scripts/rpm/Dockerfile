FROM centos:8

ARG AZURE_STORAGE_CONNECTION_STRING
ARG MSSQL_CLI_OFFICIAL_BUILD

ENV AZURE_STORAGE_CONNECTION_STRING=$AZURE_STORAGE_CONNECTION_STRING
ENV MSSQL_CLI_OFFICIAL_BUILD=$MSSQL_CLI_OFFICIAL_BUILD
RUN echo "connection string: ${AZURE_STORAGE_CONNECTION_STRING}"
RUN echo "official build: ${MSSQL_CLI_OFFICIAL_BUILD}"

# Install dependencies
RUN yum update -y
RUN yum install -y git sudo wget python3

# Upgrade pip
RUN python3 -m pip install --upgrade pip

# Build .rpm
RUN mkdir Repos
RUN mkdir Repos/mssql-cli
ADD . Repos/mssql-cli
WORKDIR Repos/mssql-cli
RUN build_scripts/rpm/build.sh $(pwd)

# Build dependencies for eventual release
RUN python3 -m pip install -r requirements-dev.txt
