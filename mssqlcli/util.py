from os import devnull
import subprocess

def encode(s):
    try:
        return s.encode('utf-8')
    except (AttributeError, SyntaxError):
        pass
    return s

# In Python 3, all strings are sequences of Unicode characters.
# There is a bytes type that holds raw bytes.
# In Python 2, a string may be of type str or of type unicode.
def decode(s):
    try:
        return s.decode('utf-8')
    except (AttributeError, SyntaxError, UnicodeEncodeError):
        pass
    return s

def is_command_valid(command):
    """
    Checks if command is recognized on machine. Used to determine installations
    of 'less' pager.
    """
    if not command:
        return False

    try:
        # call command silentyly
        with open(devnull, 'wb') as no_out:
            subprocess.call(command, stdout=no_out, stderr=no_out)
    except OSError:
        return False
    else:
        return True
