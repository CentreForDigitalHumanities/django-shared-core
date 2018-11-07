import django.utils.six as six


def string_to_bool(s):
    if s == 'None' or s is None:
        return False
    return s not in ['False', 'false', '0', 0]


def is_empty(value):
    """
    Checks if value is filled out (!= None).
    For lists and strings, also check if the value is not empty.
    """
    result = False
    if value is None:
        result = True
    if hasattr(value, '__len__') and len(value) == 0:
        result = True
    if isinstance(value, six.text_type) and not value.strip():
        result = True
    return result
