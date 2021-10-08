import re


# TODO: Add type hints

def filter_dict(predicate, mapping, *,
                by_keys_only=False, by_values_only=False):
    """Filter `mapping` by keys and/or values.

    Return a dict of items from `mapping` for which `predicate(key, value)` is
    true.
    If `by_keys_only` is true, only check `predicate(key)` for each item.
    If `by_values_only` is true, only check `predicate(value)` for each item.
    If both are true, both keys and values are checked, i.e. the function
    behaves the same as if they were both false.
    If checking by keys or values only, `predicate` must be a unary function.
    Otherwise, it must be binary.
    If `predicate` is `None`, every key/value is checked for truthiness.
    """
    if predicate is None:
        predicate = lambda *args: all(args)
    by_keys_only, by_values_only = bool(by_keys_only), bool(by_values_only)
    if by_keys_only == by_values_only:
        return {k: v for k, v in mapping.items()
                if predicate(k, v)}
    else:
        return {k: v for k, v in mapping.items()
                if predicate(k if by_keys_only else v)}


def filter_keys(predicate, mapping):
    """Filter `mapping` by keys. Calls `filter_dict(by_keys_only=True)`."""
    return filter_dict(predicate, mapping, by_keys_only=True)


def filter_values(predicate, mapping):
    """Filter `mapping` by values. Calls `filter_dict(by_values_only=True)`."""
    return filter_dict(predicate, mapping, by_values_only=True)


def not_none(value):
    """Check `value is not None`. More legible than `filter*(None, ...)`."""
    return value is not None


def parse_bool(value):
    """Convert a truthy/falsy string to the corresponding bool value."""
    value = str(value)
    if re.fullmatch(r"t(rue)?|y(es)?|on|enabled?|1", value, re.I):
        return True
    if re.fullmatch(r"f(alse)?|n(o(ne)?)?|off|disabled?|0|", value, re.I):
        return False
    raise ValueError(f"Unrecognized truth value {value}")
