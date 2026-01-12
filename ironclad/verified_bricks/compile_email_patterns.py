import re

def compile_email_patterns(patterns):
    """Compile a list of email patterns into regex objects.

    Parameters
    ----------
    patterns : Iterable[str]
        An iterable of string patterns. Each pattern is compiled into a
        :class:`re.Pattern` object with the ``re.IGNORECASE`` flag set.

    Returns
    -------
    List[re.Pattern]
        A list of compiled regex objects corresponding to the input patterns.

    Raises
    ------
    re.error
        If any pattern is an invalid regular expression.
    """
    compiled = []
    for pat in patterns:
        # Compile each pattern with case‑insensitive flag
        compiled.append(re.compile(pat, re.IGNORECASE))
    return compiled
