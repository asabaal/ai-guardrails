import pytest
from get_prime_factors import get_prime_factors

def test_case_1():
    assert get_prime_factors(28) == [2, 2, 7]

def test_nonpositive_raises():
    with pytest.raises(ValueError):
        get_prime_factors(0)
    with pytest.raises(ValueError):
        get_prime_factors(-10)
    with pytest.raises(ValueError):
        get_prime_factors(1)