# Test escape function functionality

import pytest
import sys
sys.path.insert(0, 'src')
from ironclad_ai_guardrails.code_utils import _escape_invalid_backslashes

def test_escape_backslash_simple():
    """Test simple backslash escape"""
    result = _escape_invalid_backslashes('test\\')
    # The function should escape the backslash to prevent JSON parsing errors
    # For input 'test\\', expected output is 'test\\\\'
    assert result == 'test\\\\'
    print("PASS: Simple backslash escaped correctly")

def test_escape_backslash_with_quote():
    """Test backslash before quote"""
    result = _escape_invalid_backslashes('\\"test\"')
    # The function should escape both backslash and quote
    assert result == '\\"test\"'
    print("PASS: Backslash and quote escaped correctly")

def test_escape_u_char():
    """Test \\u character handling"""
    result = _escape_invalid_backslashes('\\u_test')
    # Function should NOT convert \\u to \\\u
    assert 'u' in result
    assert '\\' not in result

def test_empty_string():
    """Test empty string"""
    result = _escape_invalid_backslashes('')
    assert result == ''
    print("PASS: Empty string handled correctly")
