# Builds .deb and installs dependencies to support release
FROM ubuntu:16.04

ARG AZURE_STORAGE_CONNECTION_STRING
ARG MSSQL_CLI_OFFICIAL_BUILD

ENV AZURE_STORAGE_CONNECTION_STRING=$AZURE_STORAGE_CONNECTION_STRING
ENV MSSQL_CLI_OFFICIAL_BUILD=$MSSQL_CLI_OFFICIAL_BUILD
RUN echo "connection string: ${AZURE_STORAGE_CONNECTION_STRING}"
RUN echo "official build: ${MSSQL_CLI_OFFICIAL_BUILD}"

RUN apt-get update
RUN apt-get -y install python3-all python3-pip python3-setuptools nano git sudo wget libssl-dev libffi-dev debhelper

# Install pip and stdeb
RUN python3 -m pip install --upgrade pip

# Build .deb
RUN mkdir Repos
RUN mkdir Repos/mssql-cli
ADD . Repos/mssql-cli
WORKDIR Repos/mssql-cli
RUN build_scripts/debian/build.sh $(pwd)

# Build dependencies to support publishing release of .deb
RUN python3 -m pip install -r requirements-dev.txt
