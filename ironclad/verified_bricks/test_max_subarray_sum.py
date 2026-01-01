from max_subarray_sum import max_subarray_sum
import pytest

def test_max_subarray_sum():
    assert max_subarray_sum([1, 2, 3]) == 6
    assert max_subarray_sum([-5, 4, -3, 4, -1, 2, 1]) == 7
    assert max_subarray_sum([-2, -3, -1, -4]) == -1
    assert max_subarray_sum([5]) == 5
    assert max_subarray_sum([-5]) == -5
    with pytest.raises(ValueError):
        max_subarray_sum([])
