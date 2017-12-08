def get_schemas():
    """
    Query string to retrieve schema names.
    :return: string
    """
    return '''
        SELECT name
        FROM sys.schemas
        ORDER BY 1'''


def get_databases():
    """
    Query string to retrieve all database names.
    :return: string
    """
    return '''
        Select name
        FROM sys.databases
        ORDER BY 1'''


def get_table_columns():
    """
    Query string to retrieve all table columns.
    :return: string
    """
    return '''
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
                FROM information_schema.columns
            )   AS isc
            INNER JOIN
            (
                SELECT  table_schema,
                        table_name
                FROM information_schema.tables
                WHERE TABLE_TYPE = 'BASE TABLE'
            )   AS ist
            ON ist.table_name = isc.table_name AND ist.TABLE_SCHEMA = isc.TABLE_SCHEMA
            ORDER BY 1, 2'''


def get_view_columns():
    """
    Query string to retrieve all view columns.
    :return: string
    """
    return '''
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
                FROM information_schema.columns
            )   AS isc
            INNER JOIN
            (
                SELECT  table_schema,
                        table_name
                FROM information_schema.tables
                WHERE TABLE_TYPE = 'VIEW'
            )   AS ist
            ON ist.table_name = isc.table_name AND ist.TABLE_SCHEMA = isc.TABLE_SCHEMA
            ORDER BY 1, 2'''


def get_views():
    """
    Query string to retrieve all views.
    :return: string
    """
    return '''
        SELECT  table_schema,
                table_name
        FROM information_schema.tables
        WHERE table_type = 'View'
        ORDER BY 1, 2'''


def get_tables():
    """
    Query string to retrive all tables.
    :return: string
    """
    return '''
        SELECT  table_schema,
                table_name
        FROM information_schema.tables
        WHERE table_type = 'BASE TABLE'
        ORDER BY 1, 2'''


def get_user_defined_types():
    """
    Query string to retrieve all user defined types.
    :return: string
    """
    return '''
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


def get_functions():
    """
    Query string to retrieve stored procedures and functions.
    :return: string
    """
    return '''
        SELECT specific_schema, specific_name
        FROM information_schema.routines
        ORDER BY 1, 2'''


def get_foreignkeys():
    """
    Query string for returning foreign keys.
    :return: string
    """
    return '''
        SELECT
            kcu1.table_schema AS fk_table_schema,
            kcu1.table_name AS fk_table_name,
            kcu1.column_name AS fk_column_name,
            kcu2.table_schema AS referenced_table_schema,
            kcu2.table_name AS referenced_table_name,
            kcu2.column_name AS referenced_column_name
        FROM information_schema.referential_constraints AS rc
        INNER JOIN information_schema.key_column_usage AS kcu1
            ON kcu1.constraint_catalog = rc.constraint_catalog
            AND kcu1.constraint_schema = rc.constraint_schema
            AND kcu1.constraint_name = rc.constraint_name
        INNER JOIN information_schema.key_column_usage AS kcu2
            ON kcu2.constraint_catalog = rc.unique_constraint_catalog
            AND kcu2.constraint_schema = rc.unique_constraint_schema
            AND kcu2.constraint_name = rc.unique_constraint_name
            AND kcu2.ordinal_position = kcu1.ordinal_position
            ORDER BY 3, 4'''
