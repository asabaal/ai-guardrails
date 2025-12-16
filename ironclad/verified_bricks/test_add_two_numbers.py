import pytest
from add_two_numbers import add_two_numbers

def test_add_positive():
    assert add_two_numbers(2, 3) == 5

def test_add_negative():
    assert add_two_numbers(-5, -10) == -15

def test_add_zero():
    assert add_two_numbers(0, 0) == 0

def test_add_float():
    assert add_two_numbers(0.5, 1.5) == 2.0

def test_add_mixed_int_float():
    assert add_two_numbers(2, 3.5) == 5.5

def test_add_large_numbers():
    assert add_two_numbers(10**18, 10**18) == 2*10**18

def test_type_error_string():
    with pytest.raises(TypeError):
        add_two_numbers('a', 1)

def test_type_error_none():
    with pytest.raises(TypeError):
        add_two_numbers(None, 1)

def test_type_error_list():
    with pytest.raises(TypeError):
        add_two_numbers([1, 2], 3)