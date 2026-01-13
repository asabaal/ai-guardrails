def list_to_dict_by_id(items):
    if not isinstance(items, list):
        raise TypeError('Expected list')
    result = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        item_id = item.get('id')
        if item_id is None:
            continue
        result[item_id] = item
    return result
