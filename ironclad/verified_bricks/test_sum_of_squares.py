import pytest
from sum_of_squares import sum_of_squares

def test_sum_of_squares():
    assert sum_of_squares([1, 2, 3]) == 14
    assert sum_of_squares([]) == 0
    assert sum_of_squares([1.5, -2]) == 1.5 * 1.5 + (-2) * (-2)
    with pytest.raises(TypeError):
        sum_of_squares([1, "a"])
    with pytest.raises(TypeError):
        sum_of_squares(None)
    with pytest.raises(TypeError):
        sum_of_squares("123")
    assert sum_of_squares([0]) == 0
    assert sum_of_squares([10**12]) == 10**24