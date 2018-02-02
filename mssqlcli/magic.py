from .main import MssqlCli
import sql.parse
import sql.connection
import logging

_logger = logging.getLogger(__name__)


def load_ipython_extension(ipython):
    """This is called via the ipython command '%load_ext mssqlcli.magic'"""

    # first, load the sql magic if it isn't already loaded
    if not ipython.find_line_magic('sql'):
        ipython.run_line_magic('load_ext', 'sql')

    # register our own magic
    ipython.register_magic_function(mssqlcli_line_magic, 'line', 'mssqlcli')


def mssqlcli_line_magic(line):
    _logger.debug('mssqlcli magic called: %r', line)
    parsed = sql.parse.parse(line, {})
    conn = sql.connection.Connection.get(parsed['connection'])

    try:
        # A corresponding mssqlcli object already exists
        mssqlcli = conn._mssqlcli
        _logger.debug('Reusing existing mssqlcli')
    except AttributeError:
        # I can't figure out how to get the underylying psycopg2 connection
        # from the sqlalchemy connection, so just grab the url and make a
        # new connection
        mssqlcli = MssqlCli()
        u = conn.session.engine.url
        _logger.debug('New mssqlcli: %r', str(u))

        mssqlcli.connect(u.database, u.host, u.username, u.port, u.password)
        conn._mssqlcli = mssqlcli

    # For convenience, print the connection alias
    print('Connected: {}'.format(conn.name))

    try:
        mssqlcli.run_cli()
    except SystemExit:
        pass

    if not mssqlcli.query_history:
        return

    q = mssqlcli.query_history[-1]

    if not q.successful:
        _logger.debug('Unsuccessful query - ignoring')
        return

    if q.meta_changed or q.db_changed or q.path_changed:
        _logger.debug('Dangerous query detected -- ignoring')
        return

    ipython = get_ipython()
    return ipython.run_cell_magic('sql', line, q.query)