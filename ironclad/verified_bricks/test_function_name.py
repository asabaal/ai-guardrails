from function_name import is_palindrome

def test_is_palindrome():
    assert is_palindrome("A man, a plan, a canal: Panama")
    assert not is_palindrome("Race a car")
    assert is_palindrome("")  # empty string
    assert is_palindrome("!!!")  # only non-alphanumeric
    assert is_palindrome("Madam")
    assert not is_palindrome("Hello")
