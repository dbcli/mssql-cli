import logging
import click
import shlex
import re
import sqlparse
from .main import special_command
from .namedqueries import named_queries

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
def list_views(mssqlcliclient, pattern, verbose):
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


@special_command('\\df', '\\df[+] [pattern]', 'List functions.')
def list_functions(mssqlcliclient, pattern, verbose):
    base_query = '''
SELECT {cols}
  FROM sys.sql_modules m
INNER JOIN sys.objects o
        ON m.object_id=o.object_id
WHERE type_desc like '%function%' {pattern}
'''

    if verbose:
        base_query = base_query.format(cols='name, type_desc', pattern='{pattern}')
    else:
        base_query = base_query.format(cols='name', pattern='{pattern}')
    if pattern:
        base_query = base_query.format(pattern='and name like \'%{0}%\''.format(pattern))
    else:
        base_query = base_query.format(pattern='')

    return mssqlcliclient.execute_multi_statement_single_batch(base_query)


@special_command('\\sf', '\\sf FUNCNAME', 'Show a function\'s definition.')
def show_function_definition(mssqlcliclient, pattern, verbose):
    if not pattern:
        click.secho('FUNCNAME is required. Usage \'\\sf FUNCNAME\'.', err=True, fg='red')
        return []
    base_query = '''
SELECT definition
  FROM sys.sql_modules m
INNER JOIN sys.objects o
        ON m.object_id=o.object_id
WHERE type_desc like '%function%' and name like '{0}'
'''.format(pattern)

    return mssqlcliclient.execute_multi_statement_single_batch(base_query)


@special_command('describe', 'DESCRIBE OBJECT', '', hidden=True, case_sensitive=False)
@special_command('\\d', '\\d OBJECT', 'List or describe database objects. Calls sp_help.')
def describe_object(mssqlcliclient, pattern, verbose):
    if not pattern:
        click.secho('OBJECT is required. Usage \'\\d OBJECT\'.', err=True, fg='red')
        return []

    base_query = 'exec sp_help [{0}]'.format(pattern)
    return mssqlcliclient.execute_multi_statement_single_batch(base_query)


@special_command('\\dl', '\\dl[+] [pattern]', 'Show logins and associated roles.')
def list_logins(mssqlcliclient, pattern, verbose):
    base_query = '''
SELECT {cols}
FROM sys.server_principals
WHERE TYPE IN ('U', 'S', 'G')
and name not like '%##%' {pattern}
ORDER BY name, type_desc
'''

    if verbose:
        base_query = base_query.format(cols='name, type_desc, default_database_name, type, create_date',
                                       pattern='{pattern}')
    else:
        base_query = base_query.format(cols='name, type_desc', pattern='{pattern}')
    if pattern:
        base_query = base_query.format(pattern='and name like \'%{0}%\''.format(pattern))
    else:
        base_query = base_query.format(pattern='')

    return mssqlcliclient.execute_multi_statement_single_batch(base_query)


@special_command('\\n', '\\n[+] [name] [param1 param2 ...]', 'List or execute named queries.')
def execute_named_query(mssqlcliclient, pattern, **__):
    if pattern == '':
        return list_named_queries(True)

    params = shlex.split(pattern)
    pattern = params.pop(0)

    query = named_queries.get(pattern)
    if query is None:
        message = "No named query: {}".format(pattern)
        return [(None, None, message, None, False)]
    else:
        query, arg_error = subst_favorite_query_args(query, params)
        if arg_error:
            return [(None, None, arg_error, None, False)]
        else:
            return mssqlcliclient.execute_multi_statement_single_batch(query)


@special_command('\\ns', '\\ns name query', 'Save a named query.')
def save_favorite_query(pattern, **_):
    """Save a new favorite query.
    Returns (rows, cols, status, sql, is_error)"""

    usage = 'Syntax: \\ns name query.\n\n' + named_queries.usage
    if not pattern:
        return [(None, None, usage, None, False)]

    name, _, query = pattern.partition(' ')

    # If either name or query is missing then print the usage and complain.
    if (not name) or (not query):
        return [(None, None, usage + 'Err: Both name and query are required.', None, False)]

    named_queries.save(name, query)
    return [(None, None, "Saved.", None, False)]


@special_command('\\nd', '\\nd [name]', 'Delete a named query.')
def delete_named_query(pattern, **_):
    """Delete an existing named query.
    """
    usage = 'Syntax: \\nd name.\n\n' + named_queries.usage
    if not pattern:
        return [(None, None, usage, None, False)]

    status = named_queries.delete(pattern)

    return [(None, None, status, None, False)]


def list_named_queries(verbose):
    """List of all named queries.
    Returns (rows, cols, status, sql, is_error)"""
    if not verbose:
        rows = [[r] for r in named_queries.list()]
        headers = ["Name"]
    else:
        headers = ["Name", "Query"]
        rows = [[r, named_queries.get(r)]
                for r in named_queries.list()]

    if not rows:
        status = named_queries.usage
    else:
        status = ''
    return [(rows, headers, status, '', False)]


def subst_favorite_query_args(query, args):
    """replace positional parameters ($1...$N) in query."""
    for idx, val in enumerate(args):
        subst_var = '$' + str(idx + 1)
        if subst_var not in query:
            return [None, 'query does not have substitution parameter ' + subst_var + ':\n  ' + query]

        query = query.replace(subst_var, val)

    match = re.search('\\$\d+', query)
    if match:
        return[None, 'missing substitution for ' + match.group(0) + ' in query:\n  ' + query]

    return [query, None]
