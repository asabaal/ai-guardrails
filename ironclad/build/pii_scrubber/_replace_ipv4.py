def _replace_ipv4(text: str) -> str:
    import re
    pattern = r'\b(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)(?:\.(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)){3}\b'
    return re.sub(pattern, '[REDACTED]', text)
