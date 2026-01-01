import pytest
from palindrome import is_palindrome

def test_is_palindrome():
    assert is_palindrome("radar")
    assert not is_palindrome("hello")
    assert is_palindrome("")
    assert is_palindrome("A")
    with pytest.raises(TypeError):
        is_palindrome(123)
