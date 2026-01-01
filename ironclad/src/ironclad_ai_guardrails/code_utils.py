#!/usr/bin/env python3
"""
Utility functions for robust code cleaning and formatting.
Ensures proper newline handling in generated code.
"""

import json
import re
from typing import Any


_VALID_JSON_ESCAPES = set(['"', "\\", "/", "b", "f", "n", "r", "t"])


def decode_newlines_in_text(text: str) -> str:
    """
    Decode escaped newline characters in text.
    Converts \\n to actual newline characters.
    Also handles escaped quotes and carriage returns.
    """
    if not isinstance(text, str):
        return text
    return text.replace("\\n", "\n").replace("\\r", "\r").replace('\\"', '"')


def decode_newlines_recursive(obj: Any) -> Any:
    if isinstance(obj, str):
        return decode_newlines_in_text(obj)
    if isinstance(obj, dict):
        return {k: decode_newlines_recursive(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [decode_newlines_recursive(item) for item in obj]
    return obj


def _strip_markdown_fences(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json|python)?\\n?", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\\n?```$", "", cleaned)
        # Also handle cases with real newlines
        cleaned = re.sub(r"^```(?:json|python)?\n?", "", cleaned, flags=re.IGNORECASE | re.MULTILINE)
        cleaned = re.sub(r"\n?```$", "", cleaned)
    return cleaned.strip()


def _escape_invalid_backslashes(s: str) -> str:
    """
    Make JSON parseable by escaping invalid backslash sequences.
    Example: "\\_" becomes "\\\\_"
    """
    out = []
    i = 0
    in_string = False
    escape = False

    while i < len(s):
        ch = s[i]

        if not in_string:
            if ch == '"':
                in_string = True
            out.append(ch)
            i += 1
            continue

        # Inside a JSON string
        if escape:
            # We already emitted a backslash, now decide what to do with the escaped char
            if ch in _VALID_JSON_ESCAPES:
                out.append(ch)
            elif ch == "u":
                # Keep \u, let json validator handle bad hex if any
                out.append("u")
            else:
                # Invalid escape, we want the backslash to be literal
                # We emitted one backslash already, add another to escape it
                out.append("\\")
                out.append(ch)
            escape = False
            i += 1
            continue

        if ch == "\\":
            out.append("\\")
            escape = True
            i += 1
            continue

        if ch == '"':
            in_string = False
            out.append(ch)
            i += 1
            continue

        out.append(ch)
        i += 1

    return "".join(out)


def clean_json_response(response_text: str) -> str:
    """
    Removes markdown fences and normalizes escape sequences.
    Returns a cleaned JSON string ready for parsing.
    """
    if not isinstance(response_text, str):
        return str(response_text)

    cleaned = _strip_markdown_fences(response_text)

    # First attempt
    try:
        parsed = json.loads(cleaned)
        parsed = decode_newlines_recursive(parsed)
        return json.dumps(parsed, ensure_ascii=False)
    except Exception:
        pass

    # Second attempt, fix invalid escapes inside strings
    cleaned2 = _escape_invalid_backslashes(cleaned)
    try:
        parsed = json.loads(cleaned2)
        parsed = decode_newlines_recursive(parsed)
        return json.dumps(parsed, ensure_ascii=False)
    except Exception:
        # Last resort, at least decode \n so callers can see real newlines
        return decode_newlines_in_text(cleaned2)


def clean_code_content(code: str) -> str:
    if not isinstance(code, str):
        return str(code)

    cleaned = decode_newlines_in_text(code)
    cleaned = _strip_markdown_fences(cleaned)

    cleaned = cleaned.strip("\n")
    # Ensure exactly one trailing newline
    return cleaned + "\n" if cleaned else ""


def validate_python_syntax(code: str) -> tuple[bool, str]:
    try:
        import ast
        ast.parse(code)
        return True, ""
    except SyntaxError as e:
        return False, f"Syntax error at line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Validation error: {e}"


def sanitize_json_content(obj: Any) -> Any:
    """
    Sanitize JSON content by decoding newlines recursively.
    This is the same as decode_newlines_recursive but with a clearer name.
    """
    return decode_newlines_recursive(obj)


def fix_common_code_issues(code: str) -> str:
    """
    Preserve real newlines and indentation.
    Remove leading blank lines, normalize line endings, trim trailing spaces.
    """
    if not isinstance(code, str):
        code = str(code)

    cleaned = decode_newlines_in_text(code)
    cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")

    # Remove leading blank lines
    cleaned = re.sub(r"^\s*\n+", "", cleaned)

    # Trim trailing spaces per line and filter out whitespace-only lines
    lines = [ln.rstrip() for ln in cleaned.split("\n") if ln.strip() != ""]

    # Collapse multiple consecutive blank lines into max one
    out_lines = []
    blank_run = 0
    for ln in lines:
        if ln == "":
            blank_run += 1
            if blank_run <= 1:
                out_lines.append("")
        else:
            blank_run = 0
            out_lines.append(ln)

    result = "\n".join(out_lines).strip("\n")
    return result + "\n" if result else ""


def extract_code_from_response(response: str) -> str:
    """
    Extract code blocks if present.
    If none found, return the original response exactly.
    """
    if not isinstance(response, str):
        return str(response)

    code_blocks = re.findall(
        r"```(?:python)?\s*\n?(.*?)\n?```",
        response,
        re.DOTALL | re.IGNORECASE,
    )
    if code_blocks:
        return clean_code_content("\n".join(code_blocks))

    # Look for Python patterns anywhere in the text, including inline
    pythonish = re.search(r"(?:^|\n|\s)(def\s+\w+|import\s+\w+|from\s+\w+\s+import)", response)
    if pythonish:
        return clean_code_content(response[pythonish.start():])

    return response
