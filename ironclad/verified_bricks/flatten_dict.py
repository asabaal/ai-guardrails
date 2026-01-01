def flatten_dict(d, parent_key='', sep='.'):
    """Flatten a nested dictionary.
    Returns a new dictionary with dot-separated keys.
    """
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict) and v:
            items.update(flatten_dict(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items
