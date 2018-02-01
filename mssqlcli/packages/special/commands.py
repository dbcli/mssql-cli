import logging
from .main import special_command, RAW_QUERY, PARSED_QUERY, NO_QUERY

logger = logging.getLogger('mssqlcli.commands')


@special_command('\\l', '\\l[+] [pattern]', 'List databases', aliases=('\\list',))
def list_databases(mssqlcliclient, pattern, verbose):
    base_query = u'select {0} from sys.databases'
    if verbose:
        base_query = base_query.format('name, create_date, compatibility_level, collation_name')
    else:
        base_query = base_query.format('name')
    if pattern:
        base_query += " where name like '%{0}%'".format(pattern)

    return mssqlcliclient.execute_multi_statement_single_batch(base_query)