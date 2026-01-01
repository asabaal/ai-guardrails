import pytest
from sum_of_even import sum_of_even

def test_sum_of_even():
    # basic case
    assert sum_of_even([1, 2, 3, 4]) == 6
    # empty list
    assert sum_of_even([]) == 0
    # includes zero and negative
    assert sum_of_even([0, -2, 5]) == -2
    # type checks
    with pytest.raises(TypeError):
        sum_of_even("123")
    with pytest.raises(TypeError):
        sum_of_even([1, "2", 3])
