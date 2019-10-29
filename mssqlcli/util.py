def encode(s):
    try:
        return s.encode('utf-8')
    except:
        pass
    return s

# In Python 3, all strings are sequences of Unicode characters.
# There is a bytes type that holds raw bytes.
# In Python 2, a string may be of type str or of type unicode.
def decode(s):
    try:
        return s.decode('utf-8')
    except:
        pass    
    return s
