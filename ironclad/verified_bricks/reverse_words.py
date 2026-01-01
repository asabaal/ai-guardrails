def reverse_words(s: str) -> str:
    """Return the input string with the order of words reversed.

    Words are sequences of non-whitespace characters. Leading, trailing,
    and multiple internal spaces are collapsed into single spaces in the
    output. An empty input string yields an empty output string.
    """
    if not s:
        return ''
    words = s.split()
    return ' '.join(reversed(words))
