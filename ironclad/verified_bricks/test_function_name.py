from function_name import is_palindrome
import pytest

def test_is_palindrome():
    assert is_palindrome('') is True
    assert is_palindrome('A') is True
    assert is_palindrome('Racecar') is True
    assert is_palindrome("Madam, I'm Adam") is True
    assert is_palindrome('Hello') is False
    with pytest.raises(TypeError):
        is_palindrome(123)