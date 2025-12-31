import pytest
from function_name import function_name


def test_palindrome_simple():
    assert function_name("radar") is True

def test_not_palindrome():
    assert function_name("hello") is False

def test_case_insensitive():
    assert function_name("RaceCar") is True

def test_ignore_non_alnum():
    assert function_name("A man, a plan, a canal: Panama") is True

def test_empty_string():
    assert function_name("") is True

def test_single_char():
    assert function_name("a") is True

def test_numeric_palindrome():
    assert function_name("12321") is True

def test_even_length_palindrome():
    assert function_name("1221") is True

def test_type_error():
    with pytest.raises(TypeError):
        function_name(123)
