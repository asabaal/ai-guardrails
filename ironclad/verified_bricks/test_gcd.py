from gcd import gcd

def test_gcd():
    assert gcd(48, 18) == 6
    assert gcd(-48, 18) == 6
    assert gcd(0, 5) == 5
    assert gcd(5, 0) == 5
    assert gcd(0, 0) == 0
    # additional edge cases
    assert gcd(13, 13) == 13
    assert gcd(1, 0) == 1
    assert gcd(-12, -18) == 6
    assert gcd(0, -7) == 7
