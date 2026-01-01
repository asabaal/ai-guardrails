def reverse_string(s: str) -> str:
    '''Return the reversed string. Handles None and empty strings.'''
    if s is None:
        return None
    return s[::-1]
