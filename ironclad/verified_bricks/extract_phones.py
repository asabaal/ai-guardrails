import re

def extract_phones(text: str) -> list:
    """Return a list of normalized 10‑digit phone numbers found in *text*.

    The function searches for common US phone number patterns, including
    optional country code ``+1`` or ``1``.  Each match is converted to a
    string of exactly 10 digits (area code + local number).  If the
    phone number contains a leading ``1`` as country code it is removed.

    Parameters
    ----------
    text: str
        Input string potentially containing phone numbers.

    Returns
    -------
    list
        A list of normalized phone numbers.  The list is empty if no
        numbers are found or if *text* is empty.
    """
    if not text:
        return []

    # Regular expression to match common US phone formats with optional
    # country code.  It captures the entire number part including
    # parentheses and separators.
    pattern = re.compile(
        r"\b(?:\+?1\s*[\-\.\s]?|1\s*[\-\.\s]?)?"
        r"(\(?\d{3}\)?[\-\.\s]?\d{3}[\-\.\s]?\d{4})\b"
    )

    numbers = []
    for match in pattern.finditer(text):
        raw = match.group(1)
        # Remove all non-digit characters
        digits = re.sub(r"\D", "", raw)
        # If number starts with '1' and is 11 digits, strip country code
        if len(digits) == 11 and digits.startswith('1'):
            digits = digits[1:]
        if len(digits) == 10:
            numbers.append(digits)
    return numbers