#!/usr/bin/env python3
"""
Utility functions for robust code cleaning and formatting.
Ensures proper newline handling in generated code.
"""

import json
import re
from typing import Any, Dict, List, Union


def decode_newlines_in_text(text: str) -> str:
    """
    Decode escaped newline characters in text.
    Converts \\n to actual newline characters.
    Also handles escaped quotes.
    """
    if not isinstance(text, str):
        return text
    return text.replace('\\n', '\n').replace('\\"', '"')


def decode_newlines_recursive(obj: Any) -> Any:
    """
    Recursively decode escaped newlines in all string values of a data structure.
    Handles dicts, lists, and nested structures.
    """
    if isinstance(obj, str):
        return decode_newlines_in_text(obj)
    elif isinstance(obj, dict):
        return {k: decode_newlines_recursive(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [decode_newlines_recursive(item) for item in obj]
    return obj


def clean_json_response(response_text: str) -> str:
    """
    Comprehensive JSON response cleaning function.
    Removes markdown fences and decodes all escape sequences.
    Returns a cleaned JSON string ready for parsing.
    """
    if not isinstance(response_text, str):
        return str(response_text)
    
    # Remove markdown code blocks if present
    cleaned = response_text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(json)?", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"```$", "", cleaned)
    cleaned = cleaned.strip()
    
    # Try to parse and re-serialize JSON to handle escape sequences
    try:
        parsed = json.loads(cleaned)
        decoded_obj = decode_newlines_recursive(parsed)
        return json.dumps(decoded_obj, ensure_ascii=False)
    except (json.JSONDecodeError, TypeError):
        # Fallback to manual cleaning
        return decode_newlines_in_text(cleaned)


def clean_code_content(code: str) -> str:
    """
    Clean code content by ensuring proper newlines and removing common artifacts.
    """
    if not isinstance(code, str):
        return str(code)
    
    # Decode escaped newlines
    cleaned = decode_newlines_in_text(code)
    
    # Remove any remaining markdown fences
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(python)?", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"```$", "", cleaned)
    
    # Clean up common formatting issues
    cleaned = cleaned.strip()
    
    # Ensure code ends with a single newline (common Python convention)
    if cleaned and not cleaned.endswith('\n'):
        cleaned += '\n'
    
    return cleaned


def validate_python_syntax(code: str) -> tuple[bool, str]:
    """
    Validate Python syntax without executing the code.
    Returns (is_valid, error_message).
    """
    try:
        import ast
        ast.parse(code)
        return True, ""
    except SyntaxError as e:
        return False, f"Syntax error at line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Validation error: {e}"


def fix_common_code_issues(code: str) -> str:
    """
    Fix common code formatting issues that might occur in LLM-generated code.
    """
    if not isinstance(code, str):
        return str(code)
    
    # Decode newlines first
    cleaned = decode_newlines_in_text(code)
    
    # Fix common issues
    cleaned = re.sub(r'\\r\\n', '\n', cleaned)  # Windows-style newlines
    cleaned = re.sub(r'\\r', '\n', cleaned)     # Old Mac newlines
    
    # Remove excessive blank lines at the beginning
    cleaned = re.sub(r'^\n+', '', cleaned)
    
    # Ensure proper spacing around common operators (basic approach)
    cleaned = re.sub(r'([=+\-*/])(?!=)', r' \1 ', cleaned)  # Space around operators
    cleaned = re.sub(r'\s+', ' ', cleaned)  # Collapse multiple spaces
    cleaned = re.sub(r' \n', '\n', cleaned)  # Remove spaces before newlines
    cleaned = re.sub(r'\n ', '\n', cleaned)  # Remove spaces after newlines
    
    return cleaned.strip() + ('\n' if cleaned else '')


def sanitize_json_content(content: Any) -> Any:
    """
    Sanitize JSON content to ensure all string fields have proper newlines.
    """
    if isinstance(content, dict):
        return {k: sanitize_json_content(v) for k, v in content.items()}
    elif isinstance(content, list):
        return [sanitize_json_content(item) for item in content]
    elif isinstance(content, str):
        return decode_newlines_in_text(content)
    return content


def extract_code_from_response(response: str) -> str:
    """
    Extract code content from a response that might contain explanations.
    Focuses on finding actual code blocks or code-like content.
    """
    if not isinstance(response, str):
        return str(response)
    
    # Try to extract from markdown code blocks first
    code_blocks = re.findall(r'```(?:python)?\s*\n?(.*?)\n?```', response, re.DOTALL | re.IGNORECASE)
    if code_blocks:
        return clean_code_content('\n'.join(code_blocks))
    
    # If no code blocks, look for Python-like patterns
    python_patterns = re.findall(r'(def\s+\w+\s*\([^)]*\)\s*:|import\s+\w+|from\s+\w+\s+import)', response)
    if python_patterns:
        # Find the start of code and take everything from there
        first_match = re.search(r'(def\s+\w+|import\s+\w+|from\s+\w+\s+import)', response, re.IGNORECASE)
        if first_match:
            code_start = first_match.start()
            return clean_code_content(response[code_start:])
    
    # Fallback: return cleaned response
    return clean_code_content(response)