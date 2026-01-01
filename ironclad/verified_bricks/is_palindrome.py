def is_palindrome(s: str) -> bool:
    """Return True if the string s is a palindrome, ignoring case and non-alphanumeric characters."""
    cleaned = ''.join(ch.lower() for ch in s if ch.isalnum())
    return cleaned == cleaned[::-1]
