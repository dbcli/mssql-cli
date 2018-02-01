import logging
from .main import special_command, RAW_QUERY, PARSED_QUERY, NO_QUERY

logger = logging.getLogger('mssqlcli.commands')


@special_command('\\l', '\\l[+] [pattern]', 'List databases.', aliases=('\\list',))
def list_databases(mssqlcliclient, pattern, verbose):
    base_query = u'select {0} from sys.databases'
    if verbose:
        base_query = base_query.format('name, create_date, compatibility_level, collation_name')
    else:
        base_query = base_query.format('name')
    if pattern:
        base_query += " where name like '%{0}%'".format(pattern)

    return mssqlcliclient.execute_multi_statement_single_batch(base_query)


@special_command('\\dn', '\\dn[+] [pattern]', 'List schemas.')
def list_schemas(mssqlcliclient, pattern, verbose):
    base_query = u'select {0} from sys.schemas'
    if verbose:
        base_query = base_query.format('name, schema_id, principal_id')
    else:
        base_query = base_query.format('name')
    if pattern:
        base_query += " where name like '%{0}%'".format(pattern)

    return mssqlcliclient.execute_multi_statement_single_batch(base_query)


@special_command('\\dt', '\\dt[+] [pattern]', 'List tables.')
def list_tables(mssqlcliclient, pattern, verbose):
    base_query = u'select {0} from INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE=\'BASE TABLE\''
    if verbose:
        base_query = base_query.format('*')
    else:
        base_query = base_query.format('table_schema, table_name')
    if pattern:
        base_query += "and table_name like '%{0}%'".format(pattern)

    return mssqlcliclient.execute_multi_statement_single_batch(base_query)