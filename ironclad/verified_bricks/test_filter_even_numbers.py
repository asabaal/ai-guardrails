def test_filter_even_numbers():
    import pytest
    from filter_even_numbers import filter_even_numbers
    assert filter_even_numbers([1, 2, 3, 4]) == [2, 4]
    assert filter_even_numbers([]) == []
    assert filter_even_numbers([0, -2, 3]) == [0, -2]
    assert filter_even_numbers([2.0, 3.0]) == []
    with pytest.raises(TypeError):
        filter_even_numbers(None)
