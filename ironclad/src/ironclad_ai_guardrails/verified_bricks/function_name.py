def function_name(s):
    if not isinstance(s, str):
        raise TypeError("Input must be a string")
    filtered = ''.join(ch.lower() for ch in s if ch.isalnum())
    return filtered == filtered[::-1]