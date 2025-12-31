import pytest

from function_name import function_name

def test_function_name():
    assert function_name(0) == 1
    assert function_name(1) == 1
    assert function_name(5) == 120
    assert function_name(10) == 3628800
    assert function_name(20) == 2432902008176640000
    with pytest.raises(TypeError):
        function_name(3.5)
    with pytest.raises(ValueError):
        function_name(-1)
