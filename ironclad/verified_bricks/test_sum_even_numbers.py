import pytest
from sum_even_numbers import sum_even_numbers

def test_sum_even_numbers():
    assert sum_even_numbers([1, 2, 3, 4, 5]) == 6
    assert sum_even_numbers([]) == 0
    assert sum_even_numbers([1, 3, 5]) == 0
    assert sum_even_numbers([-2, -4, 1]) == -6
    assert sum_even_numbers([2, "4", 6.0, 8]) == 10
    with pytest.raises(TypeError):
        sum_even_numbers(None)
