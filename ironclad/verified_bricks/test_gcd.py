from gcd import gcd
import pytest

def test_gcd():
    assert gcd(48, 18) == 6
    assert gcd(0, 5) == 5
    assert gcd(-12, 18) == 6
    with pytest.raises(ValueError):
        gcd(0, 0)
