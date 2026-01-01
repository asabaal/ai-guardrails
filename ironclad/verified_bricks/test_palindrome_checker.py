def test_is_palindrome():
    from palindrome_checker import is_palindrome
    assert is_palindrome('') == True
    assert is_palindrome('a') == True
    assert is_palindrome('Racecar') == True
    assert is_palindrome('A man, a plan, a canal: Panama') == True
    assert is_palindrome('Hello') == False
    assert is_palindrome('12321') == True
    assert is_palindrome('12 3 21') == True
    assert is_palindrome('!!!') == True
    assert is_palindrome('😀😃😄😃😀') == True
    assert is_palindrome('😀😃😄😅😀') == False
