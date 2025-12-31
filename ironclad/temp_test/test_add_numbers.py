import pytest
import sys
import os
sys.path.append(os.getcwd())
from add_numbers import add_numbers

def test_add_integers():
    assert add_numbers(2, 3) == 5

def test_add_floats():
    assert add_numbers(2.5, 3.1) == pytest.approx(5.6)

def test_add_zero():
    assert add_numbers(0, 0) == 0
    assert add_numbers(0, 5) == 5
    assert add_numbers(-5, 0) == -5

def test_add_large_numbers():
    large = 10**100
    assert add_numbers(large, large) == large * 2

def test_add_negative_numbers():
    assert add_numbers(-3, -7) == -10
    assert add_numbers(-3, 7) == 4

def test_add_type_error():
    with pytest.raises(TypeError):
        add_numbers("1", 2)
    with pytest.raises(TypeError):
        add_numbers([1], 2)
