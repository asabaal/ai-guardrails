import pytest
from is_palindrome import is_palindrome

@pytest.mark.parametrize(
    "input_str,expected",
    [
        ("", True),
        ("a", True),
        ("ab", False),
        ("aa", True),
        ("A man, a plan, a canal: Panama", True),
        ("No 'x' in Nixon", True),
        ("Was it a car or a cat I saw?", True),
        ("12321", True),
        ("12345", False),
        ("12321a", False),
        ("   ", True),
    ],
)
def test_is_palindrome(input_str, expected):
    assert is_palindrome(input_str) == expected

def test_none_input():
    with pytest.raises(TypeError):
        is_palindrome(None)
