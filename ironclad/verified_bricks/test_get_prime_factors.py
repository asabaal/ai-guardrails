import pytest
from get_prime_factors import get_prime_factors

def test_invalid_inputs():
    with pytest.raises(ValueError):
        get_prime_factors(0)
    with pytest.raises(ValueError):
        get_prime_factors(-5)
    with pytest.raises(ValueError):
        get_prime_factors(3.5)
    with pytest.raises(ValueError):
        get_prime_factors("15")

def test_valid_inputs():
    assert get_prime_factors(1) == []
    assert get_prime_factors(2) == [2]
    assert get_prime_factors(12) == [2, 2, 3]
    assert get_prime_factors(60) == [2, 2, 3, 5]