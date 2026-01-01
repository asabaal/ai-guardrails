import pytest

from is_palindrome import is_palindrome

def test_is_palindrome():
    assert is_palindrome('Racecar')
    assert is_palindrome('No lemon, no melon')
    assert not is_palindrome('Hello')
    assert is_palindrome('')
    assert is_palindrome('A')
    assert is_palindrome('0')
    assert is_palindrome('12 21')
    with pytest.raises(TypeError):
        is_palindrome(None)
