import pytest

from fib import fib

def test_fib():
    assert fib(0) == 0
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(3) == 2
    assert fib(10) == 55
    assert fib(30) == 832040
    with pytest.raises(ValueError):
        fib(-5)
