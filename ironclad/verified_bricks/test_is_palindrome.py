def test_is_palindrome():
    import pytest
    from is_palindrome import is_palindrome
    assert is_palindrome('Madam') is True
    assert is_palindrome('Racecar') is True
    assert is_palindrome('Hello') is False
    assert is_palindrome('') is True
    assert is_palindrome('A') is True
    assert is_palindrome('A man, a plan, a canal: Panama') is True
    assert is_palindrome('Was it a car or a cat I saw?') is True
    with pytest.raises(TypeError):
        is_palindrome(123)
