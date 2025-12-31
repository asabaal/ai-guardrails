def reverse_words(s: str) -> str:
    """Return a string with the order of words reversed.

    A *word* is a maximal sequence of non‑space characters.  Consecutive
    spaces are treated as a single separator in the output – the original
    spacing is ignored.  Leading and trailing spaces are removed.

    Parameters
    ----------
    s: str
        The input string.

    Returns
    -------
    str
        The string with the words in reverse order.

    Examples
    --------
    >>> reverse_words("Hello world")
    'world Hello'
    >>> reverse_words("  one   two  ")
    'two one'
    """
    # Split on any amount of whitespace, ignoring leading/trailing spaces.
    words = s.split()
    # Reverse the list of words.
    reversed_words = words[::-1]
    # Join them back together with a single space.
    return " ".join(reversed_words)
