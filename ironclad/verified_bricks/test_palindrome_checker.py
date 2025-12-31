import pytest
from palindrome_checker import is_palindrome

def test_is_palindrome():
    assert is_palindrome('RaceCar') is True
    assert is_palindrome('hello') is False
    assert is_palindrome('') is True
    assert is_palindrome('A') is True
    assert is_palindrome('Able was I ere I saw Elba') is True
    with pytest.raises(TypeError):
        is_palindrome(123)
