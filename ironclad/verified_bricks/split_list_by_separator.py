def split_list_by_separator(lst, separator):
    '''Split a list into sublists separated by separator value.'''
    if not lst:
        return []
    if separator is None:
        return [lst]
    result = []
    current = []
    for item in lst:
        if item == separator:
            result.append(current)
            current = []
        else:
            current.append(item)
    result.append(current)
    return result
