def reverse_words(s):
    if not isinstance(s, str):
        raise TypeError('Input must be a string')
    return ' '.join(reversed(s.split()))
