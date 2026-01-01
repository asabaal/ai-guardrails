def test_calculate_average():
    from calculate_average import calculate_average
    import math
    import pytest
    # Basic cases
    assert calculate_average([1, 2, 3]) == 2
    assert calculate_average([5]) == 5
    assert math.isclose(calculate_average([1.5, 2.5, 3.5]), 2.5, rel_tol=1e-9)
    # Negative numbers
    assert calculate_average([-1, -2, -3]) == -2
    # Empty list should raise ValueError
    with pytest.raises(ValueError):
        calculate_average([])
