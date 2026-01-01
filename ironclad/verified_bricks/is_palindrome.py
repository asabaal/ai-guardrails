def is_palindrome(s):
    if not isinstance(s, str):
        raise TypeError('Input must be a string')
    cleaned = ''.join(c.lower() for c in s if c.isalnum())
    return cleaned == cleaned[::-1]
