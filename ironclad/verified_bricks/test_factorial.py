from factorial import factorial
import pytest

def test_factorial():
    assert factorial(0) == 1
    assert factorial(1) == 1
    assert factorial(5) == 120
    with pytest.raises(TypeError):
        factorial(3.5)
    with pytest.raises(ValueError):
        factorial(-1)
