def test_max_product_pair():
    from max_product_pair import max_product_pair
    import pytest
    assert max_product_pair([1, 2, 3, 4]) == 12
    assert max_product_pair([-5, -3, 4, 2]) == 15
    assert max_product_pair([0, 1]) == 0
    with pytest.raises(ValueError):
        max_product_pair([5])
    with pytest.raises(ValueError):
        max_product_pair([])
    assert max_product_pair([1.5, 2, 3]) == 6
    assert max_product_pair([2, 3, -10, -10]) == 100
    assert max_product_pair([2, 2, 2]) == 4
