import pytest
from is_prime import is_prime


def test_basic_primes():
    assert is_prime(2)
    assert is_prime(3)
    assert is_prime(5)
    assert is_prime(7)


def test_basic_non_primes():
    assert not is_prime(0)
    assert not is_prime(1)
    assert not is_prime(4)
    assert not is_prime(6)
    assert not is_prime(8)


def test_edge_cases():
    assert not is_prime(-5)
    assert not is_prime(-1)
    assert not is_prime(100)
    assert not is_prime(49)


def test_large_prime():
    # 104729 is the 10000th prime
    assert is_prime(104729)


def test_non_integer_input():
    with pytest.raises(TypeError):
        is_prime(3.5)
    with pytest.raises(TypeError):
        is_prime("string")