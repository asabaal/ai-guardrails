from typing import Pattern

def replace_ipv4s(text: str, pattern: Pattern) -> str:
    return pattern.sub('[REDACTED]', text)
