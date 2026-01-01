def test_sum_of_digits():
    from sum_of_digits import sum_of_digits
    assert sum_of_digits(0) == 0
    assert sum_of_digits(12345) == 15
    assert sum_of_digits(-9876) == 30
    assert sum_of_digits(5) == 5
    assert sum_of_digits(999) == 27
