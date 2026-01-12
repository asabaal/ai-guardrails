def is_palindrome(s: str) -> bool:
    """Return True if s is a palindrome, ignoring case and non-alphanumeric characters."""
    cleaned = [c.lower() for c in s if c.isalnum()]
    return cleaned == cleaned[::-1]
