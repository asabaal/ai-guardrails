import re

def parse_input_str(input_str: str) -> float:
    if not isinstance(input_str, str):
        raise TypeError("input_str must be a string")
    s = input_str.strip()
    if not s:
        raise ValueError("empty string")
    pattern = r'^[+-]?((\d+(\.\d*)?)|(\.\d+))([eE][+-]?\d+)?$'
    if not re.fullmatch(pattern, s):
        raise ValueError(f"'{input_str}' is not a valid numeric string")
    return float(s)
