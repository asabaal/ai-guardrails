def is_palindrome(s):
    '''
    Return True if s is a palindrome, ignoring case and non-alphanumeric characters.
    Raise TypeError if s is not a string.
    '''
    if not isinstance(s, str):
        raise TypeError('Input must be a string')
    cleaned = ''.join(ch.lower() for ch in s if ch.isalnum())
    return cleaned == cleaned[::-1]
