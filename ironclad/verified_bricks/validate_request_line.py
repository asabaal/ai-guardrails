def validate_request_line(line: str) -> bool:
    """
    Validates a simple HTTP request line.
    Format: METHOD PATH HTTP/VERSION
    METHOD: uppercase letters only, e.g., GET, POST
    PATH: starts with '/' and contains any characters except space
    VERSION: major.minor, digits separated by a dot
    Returns True if line matches the pattern, False otherwise.
    """
    if not isinstance(line, str):
        return False
    import re
    pattern = r'^[A-Z]+ /[^ ]+ HTTP/\d+\.\d+$'
    return re.match(pattern, line) is not None