try:
    text_type = unicode
except NameError:
    text_type = str


def unicode2utf8(arg):
    """
    Only in Python 2.
    In Python 3 the args are expected as unicode.
    """

    try:
        if isinstance(arg, unicode):
            return arg.encode('utf-8')
    except NameError:
        pass  # Python 3
    return arg


def utf8tounicode(arg):
    """
    Only in Python 2.
    In Python 3 the errors are returned as unicode.
    """

    try:
        if isinstance(arg, unicode):
            return arg.decode('utf-8')
    except NameError:
        pass  # Python 3
    return arg
