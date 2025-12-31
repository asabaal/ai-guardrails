import pytest
from sum_of_squares_of_even_numbers import sum_of_squares_of_even_numbers

def test_sum_of_squares_of_even_numbers():
    assert sum_of_squares_of_even_numbers([1, 2, 3, 4]) == 20
    assert sum_of_squares_of_even_numbers([]) == 0
    assert sum_of_squares_of_even_numbers([1, 3, 5]) == 0
    assert sum_of_squares_of_even_numbers([-2, -4, 5]) == 20
    with pytest.raises(TypeError):
        sum_of_squares_of_even_numbers('not a list')
    with pytest.raises(TypeError):
        sum_of_squares_of_even_numbers(None)
