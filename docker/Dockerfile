# vim: set et ts=4 sw=4 ft=dockerfile:

# A basic Dockerfile for packaging up mssql-cli as a better alternative to sqlcmd.

FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive
ARG TZ=UTC
ARG LANG=en_US.UTF-8

# Make apt quiet.
RUN apt-get update && \
    LANG=C apt-get --no-install-recommends -y install locales && \
        locale-gen ${LANG} && update-locale LANG=${LANG} && \
    DEBIAN_FRONTEND=${DEBIAN_FRONTEND} TZ=${TZ} \
        apt-get --no-install-recommends -y install tzdata && \
    DEBIAN_FRONTEND=${DEBIAN_FRONTEND} TZ=${TZ} \
        dpkg-reconfigure tzdata && \
    apt-get -y clean && rm -rf /var/lib/apt/lists/*

# Install the dependent packages we need.
RUN apt-get update && \
    apt-get --no-install-recommends -y install \
        less python3 python3-pip libicu-dev && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3 1000 && \
    python3 -m pip install --no-cache-dir -U pip && \
    apt-get -y clean && rm -rf /var/lib/apt/lists/* && \
    mkdir -p /src/mssql-cli/

# Copy and install the python module for mssql-cli.
WORKDIR /src/mssql-cli/
COPY . /src/mssql-cli/
RUN python3 -m pip install --no-cache-dir -U -e /src/mssql-cli/

# Verify that the command runs.
RUN mssql-cli --help

# A few quality of life improvements:
# - Don't beep/bell on tab completion failure.
RUN echo 'set bell-style none' >> /etc/inputrc

ENV PAGER=less
ENV LESS=-iRQX

ENTRYPOINT ["/usr/local/bin/mssql-cli"]
CMD ["/usr/local/bin/mssql-cli", "--help"]
