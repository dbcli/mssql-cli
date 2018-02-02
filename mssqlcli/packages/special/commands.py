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


@special_command('\\dv', '\\dv[+] [pattern]', 'List views.')
def list_tables(mssqlcliclient, pattern, verbose):
    base_query = u'select {0} from INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE=\'VIEW\''
    if verbose:
        base_query = base_query.format('table_catalog as catalog, table_schema as schema_name, '
                                       'table_name as view_name')
    else:
        base_query = base_query.format('table_schema as schema_name, table_name as view_name')
    if pattern:
        base_query += "and table_name like '%{0}%'".format(pattern)

    return mssqlcliclient.execute_multi_statement_single_batch(base_query)


@special_command('\\di', '\\di[+] [pattern]', 'List indexes.')
def list_indexes(mssqlcliclient, pattern, verbose):
    base_query = '''
SELECT
     TableName = t.name,
     IndexName = ind.name,
     ColumnName = col.name {verbose}
FROM
     sys.indexes ind
INNER JOIN
     sys.index_columns ic ON  ind.object_id = ic.object_id and ind.index_id = ic.index_id
INNER JOIN
     sys.columns col ON ic.object_id = col.object_id and ic.column_id = col.column_id
INNER JOIN
     sys.tables t ON ind.object_id = t.object_id
WHERE
     ind.is_primary_key = 0
     AND ind.is_unique = 0
     AND ind.is_unique_constraint = 0
     AND t.is_ms_shipped = 0
     AND ind.name like '%{pattern}%'
ORDER BY
     t.name, ind.name, ind.index_id, ic.index_column_id;
    '''

    if verbose:
        base_query = base_query.format(verbose=',IndexId = ind.index_id, ColumnId = ic.index_column_id',
                                       pattern='{pattern}')
    else:
        base_query = base_query.format(verbose='', pattern='{pattern}')
    if pattern:
        base_query = base_query.format(pattern=pattern)
    else:
        base_query = base_query.format(pattern='')

    return mssqlcliclient.execute_multi_statement_single_batch(base_query)
