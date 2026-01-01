def test_sum_positive_numbers():
    from sum_positive_numbers import sum_positive_numbers
    import pytest

    assert sum_positive_numbers([1, 2, -3, 4]) == 7
    assert sum_positive_numbers([]) == 0
    assert sum_positive_numbers([0, -1, -2]) == 0
    assert sum_positive_numbers([1.5, 2.5, -1]) == 4.0

    with pytest.raises(TypeError):
        sum_positive_numbers("not a list")
    with pytest.raises(TypeError):
        sum_positive_numbers([1, 'a', 3])
