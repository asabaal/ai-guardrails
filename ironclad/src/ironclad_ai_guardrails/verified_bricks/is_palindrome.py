def is_palindrome(s):
    if not isinstance(s, str):
        raise TypeError('Input must be a string')
    import re
    cleaned = re.sub(r'[^A-Za-z0-9]', '', s).lower()
    return cleaned == cleaned[::-1]