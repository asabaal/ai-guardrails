import pytest
from find_max_subarray import find_max_subarray

def test_find_max_subarray():
    assert find_max_subarray([1, 2, 3]) == 6
    assert find_max_subarray([-1, -2, -3]) == -1
    assert find_max_subarray([2, -1, 2]) == 3
    assert find_max_subarray([5]) == 5
    with pytest.raises(ValueError):
        find_max_subarray([])
