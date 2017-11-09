import os
import pgcli.sqltoolsclient as sqltoolsclient
import pgcli.mssqlcliclient as mssqlcliclient


def create_mssql_cli_client(owner_uri=None, connect=True):
    """
    Retrieve a mssqlcliclient connection.
    :param owner_uri: string
    :param connect: boolean
    :param server_name: string
    :param database_name: string
    :return: MssqlCliClient
    """
    try:
        server_name = os.environ['MSSQLCLIHOST']
        database_name = os.environ['MSSQLCLIDATABASE']
        user_name = os.environ['MSSQLCLIUSER']
        password = os.environ['MSSQLCLIPASSWORD']

        if not server_name or not database_name or not user_name or not password:
            raise Exception('Environment variables for running tests not found.')

        sql_tools_client = sqltoolsclient.SqlToolsClient()
        mssql_cli_client = mssqlcliclient.MssqlCliClient(sql_tools_client,
                                                         server_name,
                                                         user_name,
                                                         password,
                                                         database=database_name,
                                                         owner_uri=owner_uri,
                                                         extra_bool_param=True,
                                                         extra_string_param=u'stringparam',
                                                         extra_int_param=5)
        if connect:
            mssql_cli_client.connect()
        return mssql_cli_client
    except Exception as e:
        print('Connection failed')
        raise e

def shutdown(connection):
    connection.shutdown()
