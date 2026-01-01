import pytest
from average_numbers import average_numbers

def test_average_numbers():
    assert average_numbers([1, 2, 3]) == 2.0
    assert average_numbers([10]) == 10
    assert average_numbers([-1, 1]) == 0
    with pytest.raises(ValueError):
        average_numbers([])
    with pytest.raises(TypeError):
        average_numbers([1, 'a'])
