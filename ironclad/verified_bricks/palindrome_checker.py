def is_palindrome(s: str) -> bool:
    """Return True if *s* is a palindrome, ignoring case, spaces, and punctuation.

    Emoji characters are preserved, as they are not considered punctuation.
    """
    import unicodedata
    cleaned = ''.join(
        c.lower()
        for c in s
        if not c.isspace() and not unicodedata.category(c).startswith('P')
    )
    return cleaned == cleaned[::-1]
