def test_sum_list():
    from sum_list import sum_list
    # Basic functionality
    assert sum_list([1, 2, 3]) == 6
    # Empty list
    assert sum_list([]) == 0
    # Negative numbers
    assert sum_list([-1, 1]) == 0
    # Floats
    assert sum_list([1.5, 2.5]) == 4.0
    import pytest
    # Non-list input should raise TypeError
    with pytest.raises(TypeError):
        sum_list('not a list')
    # List with non-numeric element should raise TypeError
    with pytest.raises(TypeError):
        sum_list([1, 'a'])
