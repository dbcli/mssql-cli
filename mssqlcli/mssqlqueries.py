import sys
import re

def get_schemas():
    """
    Query string to retrieve schema names.
    :return: string
    """
    sql = '''
        SELECT name
        FROM sys.schemas
        ORDER BY 1'''
    return normalize(sql)


def get_databases():
    """
    Query string to retrieve all database names.
    :return: string
    """
    sql = '''
        Select name
        FROM sys.databases
        ORDER BY 1'''
    return normalize(sql)


def get_table_columns():
    """
    Query string to retrieve all table columns.
    :return: string
    """
    sql = '''
        SELECT  isc.table_schema,
                isc.table_name,
                isc.column_name,
                isc.data_type,
                isc.column_default
        FROM
            (
                SELECT  table_schema,
                        table_name,
                        column_name,
                        data_type,
                        column_default
                FROM INFORMATION_SCHEMA.COLUMNS
            )   AS isc
            INNER JOIN
            (
                SELECT  table_schema,
                        table_name
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_TYPE = 'BASE TABLE'
            )   AS ist
            ON ist.table_name = isc.table_name AND ist.table_schema = isc.table_schema
            ORDER BY 1, 2'''
    return normalize(sql)


def get_view_columns():
    """
    Query string to retrieve all view columns.
    :return: string
    """
    sql = '''
        SELECT  isc.table_schema,
                isc.table_name,
                isc.column_name,
                isc.data_type,
                isc.column_default
        FROM
            (
                SELECT  table_schema,
                        table_name,
                        column_name,
                        data_type,
                        column_default
                FROM INFORMATION_SCHEMA.COLUMNS
            )   AS isc
            INNER JOIN
            (
                SELECT  table_schema,
                        table_name
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_TYPE = 'VIEW'
            )   AS ist
            ON ist.table_name = isc.table_name AND ist.table_schema = isc.table_schema
            ORDER BY 1, 2'''
    return normalize(sql)


def get_views():
    """
    Query string to retrieve all views.
    :return: string
    """
    sql = '''
        SELECT  table_schema,
                table_name
        FROM INFORMATION_SCHEMA.VIEWS
        ORDER BY 1, 2'''
    return normalize(sql)


def get_tables():
    """
    Query string to retrive all tables.
    :return: string
    """
    sql = '''
        SELECT  table_schema,
                table_name
        FROM INFORMATION_SCHEMA.TABLES
        WHERE table_type = 'BASE TABLE'
        ORDER BY 1, 2'''
    return normalize(sql)


def get_user_defined_types():
    """
    Query string to retrieve all user defined types.
    :return: string
    """
    sql = '''
        SELECT  schemas.name,
                types.name
        FROM
        (
            SELECT name,
                    schema_id
            FROM sys.types
            WHERE is_user_defined = 1) AS types
        INNER JOIN
        (
            SELECT name,
                    schema_id
            FROM   sys.schemas) AS schemas
        ON types.schema_id = schemas.schema_id'''
    return normalize(sql)


def get_functions():
    """
    Query string to retrieve stored procedures and functions.
    :return: string
    """
    sql = '''
        SELECT specific_schema, specific_name
        FROM INFORMATION_SCHEMA.ROUTINES
        ORDER BY 1, 2'''
    return normalize(sql)


def get_foreignkeys():
    """
    Query string for returning foreign keys.
    :return: string
    """
    sql = '''
        SELECT
            kcu1.table_schema AS fk_table_schema,
            kcu1.table_name AS fk_table_name,
            kcu1.column_name AS fk_column_name,
            kcu2.table_schema AS referenced_table_schema,
            kcu2.table_name AS referenced_table_name,
            kcu2.column_name AS referenced_column_name
        FROM INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS AS rc
        INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE AS kcu1
            ON kcu1.constraint_catalog = rc.constraint_catalog
            AND kcu1.constraint_schema = rc.constraint_schema
            AND kcu1.constraint_name = rc.constraint_name
        INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE AS kcu2
            ON kcu2.constraint_catalog = rc.unique_constraint_catalog
            AND kcu2.constraint_schema = rc.unique_constraint_schema
            AND kcu2.constraint_name = rc.unique_constraint_name
            AND kcu2.ordinal_position = kcu1.ordinal_position
            ORDER BY 3, 4'''
    return normalize(sql)


def normalize(sql):
    if (sql == '' or sql is None):
        return sql
    sql = sql.replace('\r', ' ').replace('\n', ' ').strip()
    sql = re.sub(r' +', ' ', sql)
    return sql.decode('utf-8') if sys.version_info[0] < 3 else sql
