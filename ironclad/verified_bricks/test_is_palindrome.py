from is_palindrome import is_palindrome

def test_is_palindrome():
    # Basic palindromes
    assert is_palindrome("radar") is True
    assert is_palindrome("Madam") is True
    # Non-palindromes
    assert is_palindrome("hello") is False
    # Edge cases: empty string and single character
    assert is_palindrome("") is True
    assert is_palindrome("a") is True
    # Ignore punctuation and spaces
    assert is_palindrome("A man, a plan, a canal: Panama") is True
    # Case sensitivity
    assert is_palindrome("RaceCar") is True
    # Numbers included
    assert is_palindrome("12321") is True
    assert is_palindrome("12345") is False
