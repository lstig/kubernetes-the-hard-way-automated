import re

FILTERS = {}

def filter(func):
    FILTERS[func.__name__] = func
    return func

@filter
def get_dict_value(d, *keys):
    """Safely looks up arbitrarily nested dict keys"""
    for key in keys:
        d = d.get(key, None)
    return d

@filter
def map_format(*values, pattern):
    """Performs more complex formatting on a list of values"""
    return pattern.format(*values)

@filter
def is_vault_string(str):
    '''check if string is an encrypted ansible vault'''
    pattern = r'^\$ANSIBLE_VAULT;\d+\.\d+;(AES256)'
    match   = re.match(pattern, str)
    return bool(match)

@filter
def trim_encrypt_string(str):
    '''trims output of "ansible-vault encrypt_string"'''
    str = str.splitlines(keepends=True)[1:]
    str = (line.lstrip() for line in str)
    return ''.join(str)

class FilterModule(object):
    '''custom jinja2 filters'''
    def filters(self):
        return FILTERS