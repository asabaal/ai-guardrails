def test_max_subarray_sum():
    from max_subarray_sum import max_subarray_sum
    assert max_subarray_sum([1, -2, 3, 10, -4, 7, 2, -5]) == 18
    assert max_subarray_sum([-1, -2, -3]) == -1
    assert max_subarray_sum([0, 0, 0]) == 0
    assert max_subarray_sum([]) == 0
    assert max_subarray_sum([5]) == 5
