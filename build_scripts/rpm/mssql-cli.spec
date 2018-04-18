# RPM spec file for mssql-cli
# Definition of macros used - https://fedoraproject.org/wiki/Packaging:RPMMacros?rd=Packaging/RPMMacros

%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')

# .el7.centos -> .el7
%if 0%{?rhel} == 7
  %define dist .el7
%endif

%define name           mssql-cli
%define release        1%{?dist}
%define time_stamp     %(date +%y%m%d%H%M)
%define base_version   0.10.0
%define python_dir     %{_builddir}/python_env
%define python_url     https://www.python.org/ftp/python/3.6.1/Python-3.6.1.tgz
%define cli_lib_dir    %{_libdir}/mssql-cli
%define repo_path      %{getenv:REPO_PATH}
%define official_build %{getenv:MSSQL_CLI_OFFICIAL_BUILD}

%if "%{official_build}" != "True"
  %define version %{base_version}.dev%{time_stamp}
%else
  %define version %{base_version}
%endif

AutoReq:        no
Summary:        Microsoft SQL Server CLI
License:        BSD-3
Name:           %{name}
Version:        %{version}
Release:        %{release}
Url:            https://github.com/dbcli/mssql-cli
BuildArch:      x86_64

BuildRequires:  gcc
BuildRequires:  libffi-devel
BuildRequires:  openssl-devel

Requires:       libunwind, libicu

%description
    We’re excited to introduce mssql-cli, a new and interactive command line query tool for SQL Server.
    This open source tool works cross-platform and proud to be a part of the dbcli.org community.

%prep
# Clean previous build directory.
rm -rf %{_builddir}/*
# Download, Extract Python3
python_archive=$(mktemp)
wget https://www.python.org/ftp/python/3.6.1/Python-3.6.1.tgz -qO $python_archive
tar -xvzf $python_archive -C %{_builddir}

%build
# clean any previous make files
make clean || echo "Nothing to clean"

# Build Python from source
%{_builddir}/*/configure --srcdir %{_builddir}/* --prefix %{python_dir}
make
make install

# Build mssql-cli wheel from source.
export CUSTOM_PYTHON=%{python_dir}/bin/python3
export CUSTOM_PIP=%{python_dir}/bin/pip3

%{python_dir}/bin/python3 %{repo_path}/build.py build

%install
# Install mssql-cli
dist_dir=%{repo_path}/dist
all_modules=`find $dist_dir -name "*.whl"`
%{python_dir}/bin/pip3  install $all_modules

# Create executable
mkdir -p %{buildroot}%{cli_lib_dir}
cp -a %{python_dir}/* %{buildroot}%{cli_lib_dir}
mkdir -p %{buildroot}%{_bindir}
printf "if [ -z ${PYTHONIOENCODING+x} ]; then export PYTHONIOENCODING=utf8; fi" > %{buildroot}%{_bindir}/mssql-cli
printf '#!/usr/bin/env bash\n%{cli_lib_dir}/bin/python3 -Esm mssqlcli.main "$@"' > %{buildroot}%{_bindir}/mssql-cli

%files
# Include mssql-cli directory which includes it's own python.
# Include executable mssql-cli.
%attr(0755,root,root) %{_bindir}/mssql-cli
%attr(-,root,root) %{cli_lib_dir}
