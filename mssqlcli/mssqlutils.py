import itertools

from cli_helpers.tabular_output import TabularOutputFormatter
from cli_helpers.tabular_output.preprocessors import (align_decimals,
                                                      format_numbers)

from mssqlcli.encodingutils import utf8tounicode
from mssqlcli.encodingutils import text_type


def has_meta_cmd(query):
    """Determines if the completion needs a refresh by checking if the sql
    statement is an alter, create, drop, commit or rollback."""
    try:
        first_token = query.split()[0]
        if first_token.lower() in ('alter', 'create', 'drop'):
            return True
    except Exception:
        return False

    return False


def has_change_db_cmd(query):
    """Determines if the statement is a database switch such as 'use' or '\\c'
       Returns (True, DBName) or (False, None)
    """
    try:
        first_token = query.split()[0]
        if first_token.lower() in ('use', '\\c', '\\connect'):
            return True, query.split()[1].strip('"')
    except Exception:
        return False, None

    return False, None


def has_security_statement_in_cmd(query):
    """Determines if the statement contains a PASSWORD keyword
    """
    try:
        tokens = query.lower().split()
        return 'password' in tokens

    except Exception:
        return False


def quit_command(sql):
    return (sql.strip().lower() == 'exit' or
            sql.strip().lower() == 'quit' or
            sql.strip() == r'\q' or
            sql.strip() == ':q')


def format_output(title, cur, headers, status, settings):
    output = []
    expanded = (settings.expanded or settings.table_format == 'vertical')
    table_format = ('vertical' if settings.expanded else
                    settings.table_format)
    max_width = settings.max_width
    case_function = settings.case_function
    formatter = TabularOutputFormatter(format_name=table_format)

    def format_array(val):
        if val is None:
            return settings.missingval
        if not isinstance(val, list):
            return val
        return '{' + ','.join(text_type(format_array(e)) for e in val) + '}'

    def format_arrays(data, headers, **_):
        data = list(data)
        for row in data:
            row[:] = [
                format_array(val) if isinstance(val, list) else val
                for val in row
            ]

        return data, headers

    output_kwargs = {
        'sep_title': 'RECORD {n}',
        'sep_character': '-',
        'sep_length': (1, 25),
        'missing_value': settings.missingval,
        'integer_format': settings.dcmlfmt,
        'float_format': settings.floatfmt,
        'preprocessors': (format_numbers, format_arrays),
        'disable_numparse': True,
        'preserve_whitespace': True
    }
    if not settings.floatfmt:
        output_kwargs['preprocessors'] = (align_decimals, )

    if title:
        output.append(title)

    if cur:
        headers = [case_function(utf8tounicode(x)) for x in headers]
        if max_width is not None:
            cur = list(cur)
        formatted = formatter.format_output(cur, headers, **output_kwargs)
        if isinstance(formatted, text_type):
            formatted = iter(formatted.splitlines())
        first_line = next(formatted)
        formatted = itertools.chain([first_line], formatted)

        if (not expanded and max_width and len(
                first_line) > max_width and headers):
            formatted = formatter.format_output(
                cur, headers, format_name='vertical', column_types=None, **output_kwargs)
            if isinstance(formatted, text_type):
                formatted = iter(formatted.splitlines())

        output = itertools.chain(output, formatted)

    if status:  # Only print the status if it's not None.
        output = itertools.chain(output, [status])

    return output