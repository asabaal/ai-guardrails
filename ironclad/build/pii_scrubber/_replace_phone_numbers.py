def _replace_phone_numbers(text: str) -> str:
    import re
    # Regex to match phone numbers with optional international prefix, area code, separators.
    # Enforce boundaries: not preceded by hyphen or word character, and not followed by hyphen or word character.
    pattern = re.compile(r'''
        (?<![-\w])                 # Not preceded by hyphen or alphanumeric
        (?:\+?\d{1,3}[ .-]?)?     # Optional country code
        (?:\(?\d{1,4}\)?[ .-]?)? # Optional area code
        \d{3,4}                    # First group of digits
        (?:[ .-]?\d{3,4})+         # Subsequent groups
        (?![-\w])                  # Not followed by hyphen or alphanumeric
    ''', re.VERBOSE)
    def repl(match: re.Match) -> str:
        digits = re.sub(r'\D', '', match.group(0))
        return '[REDACTED]' if 7 <= len(digits) <= 15 else match.group(0)
    return pattern.sub(repl, text)
