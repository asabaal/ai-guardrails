import pytest

from sum_of_squares import sum_of_squares

def test_sum_of_squares_normal():
    assert sum_of_squares([1, 2, 3]) == 14
    assert sum_of_squares([-1, -2]) == 5
    assert sum_of_squares([0.5, 1.5]) == 0.5 ** 2 + 1.5 ** 2

def test_sum_of_squares_empty():
    assert sum_of_squares([]) == 0

def test_sum_of_squares_invalid_input():
    with pytest.raises(TypeError):
        sum_of_squares(None)
    with pytest.raises(TypeError):
        sum_of_squares([1, "a", 3])
