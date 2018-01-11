#!/usr/bin/env python
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import io
import subprocess
import mssqlcli.mssqltoolsservice as mssqltoolsservice
import mssqlcli.jsonrpc.jsonrpcclient as json_rpc_client
import time


# Helper to generate a query baseline
#
def generate_query_baseline(file_name):
    sqltoolsservice_args = [mssqltoolsservice.get_executable_path()]
    with io.open(file_name, 'wb') as baseline:
        tools_service_process = subprocess.Popen(
            sqltoolsservice_args,
            bufsize=0,
            stdin=subprocess.PIPE,
            stdout=baseline)

        # Before running this script, enter a real server name.
        parameters = {u'OwnerUri': u'connectionservicetest',
                      u'Connection':
                          {u'ServerName': u'*',
                           u'DatabaseName': u'AdventureWorks2014',
                           u'UserName': u'*',
                           u'Password': u'*',
                           u'AuthenticationType': u'Integrated'}
                      }

        writer = json_rpc_client.JsonRpcWriter(tools_service_process.stdin)
        writer.send_request(u'connection/connect', parameters, id=1)

        time.sleep(2)

        parameters = {u'OwnerUri': u'connectionservicetest',
                      u'Query': "select * from HumanResources.Department"}
        writer.send_request(u'query/executeString', parameters, id=2)

        time.sleep(5)
        parameters = {u'OwnerUri': u'connectionservicetest',
                      u'BatchIndex': 0,
                      u'ResultSetIndex': 0,
                      u'RowsStartIndex': 0,
                      u'RowsCount': 16}

        writer.send_request(u'query/subset', parameters, id=3)
        # submit raw request.
        time.sleep(5)
        tools_service_process.kill()


if __name__ == '__main__':
    generate_query_baseline(
        "select_from_humanresources_department_adventureworks2014.txt")
