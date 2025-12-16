import pytest
from fibonacci import fibonacci

def test_fibonacci_basic():
    assert fibonacci(0) == 0
    assert fibonacci(1) == 1
    assert fibonacci(2) == 1
    assert fibonacci(5) == 5
    assert fibonacci(10) == 55

def test_fibonacci_large():
    assert fibonacci(30) == 832040
    assert fibonacci(50) == 12586269025

def test_fibonacci_negative():
    with pytest.raises(ValueError):
        fibonacci(-1)

def test_fibonacci_non_integer():
    with pytest.raises(TypeError):
        fibonacci(3.5)
