import pytest
from factorial import factorial

class TestFactorial:
    def test_positive(self):
        assert factorial(0) == 1
        assert factorial(1) == 1
        assert factorial(5) == 120

    def test_negative(self):
        with pytest.raises(ValueError):
            factorial(-1)

    def test_non_int(self):
        with pytest.raises(TypeError):
            factorial(3.5)
