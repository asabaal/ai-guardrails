import re

# Regex patterns for detecting PII
_email_regex = re.compile(r"[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}")
_ipv4_regex = re.compile(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b")
# Phone numbers: patterns with optional parentheses and various separators
# The regex ensures we do not match digits that are part of a longer number
_phone_regex = re.compile(r"(?<!\d)(?:\(\d{3}\)[\s-]?|\d{3}[-.\s]?)\d{3}[-.\s]?\d{4}(?!\d)")


def _replace_emails(text: str) -> str:
    """Replace all email addresses in the text with a placeholder."""
    return _email_regex.sub("[EMAIL REDACTED]", text)


def _replace_ipv4(text: str) -> str:
    """Replace all IPv4 addresses in the text with a placeholder."""
    return _ipv4_regex.sub("[IP REDACTED]", text)


def _replace_phone_numbers(text: str) -> str:
    """Replace all phone numbers in the text with a placeholder."""
    return _phone_regex.sub("[PHONE REDACTED]", text)


def scrub_pii(text: str) -> str:
    """Public API that sanitizes PII from the input string.

    The function validates that the input is a string, then sequentially
    replaces email addresses, IPv4 addresses, and phone numbers.  The
    replacements are idempotent – calling the function twice on the same
    string yields the same result.

    Args:
        text: The string to sanitize.

    Returns:
        The sanitized string.

    Raises:
        TypeError: If the input is not a string.
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    result = _replace_emails(text)
    result = _replace_ipv4(result)
    result = _replace_phone_numbers(result)
    return result
