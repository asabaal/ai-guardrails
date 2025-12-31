import pytest
from function_name import function_name

def test_add_integers():
    assert function_name(2, 3) == 5

def test_add_floats():
    assert function_name(2.5, 3.1) == 5.6

def test_add_negative():
    assert function_name(-1, -4) == -5

def test_add_zero():
    assert function_name(0, 5) == 5

def test_type_error_string():
    with pytest.raises(TypeError):
        function_name('a', 1)

def test_type_error_none():
    with pytest.raises(TypeError):
        function_name(None, 1)