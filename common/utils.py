import re


def filter_dict(function, mapping, by_values=False):
    """Filter mapping by keys or values.

    Return a dict of items from mapping for which either function(key)
    or function(value) is true (depending on by_values). If function is
    None, return the items whose either key or value is true.
    """
    if function is None:
        function = bool
    return {k: v for k, v in mapping.items()
            if function(v if by_values else k)}


def filter_keys(function, mapping):
    """Filter mapping by keys. Calls filter_dict with by_values=False."""
    return filter_dict(function, mapping, by_values=False)


def filter_values(function, mapping):
    """Filter mapping by values. Calls filter_dict with by_values=True."""
    return filter_dict(function, mapping, by_values=True)


def not_none(value):
    """Check that value is not None. More legible than filter*(None, ...)."""
    return value is not None


def parse_bool(value):
    """Convert a truthy/falsy string to the corresponding bool value."""
    value = str(value)
    if re.fullmatch(r"t(rue)?|y(es)?|on|enabled?|1", value, re.I):
        return True
    if re.fullmatch(r"f(alse)?|n(o(ne)?)?|off|disabled?|0|", value, re.I):
        return False
    raise ValueError(f"Unconventional truth value {value}")
