from fibonacci import fibonacci

def test_fibonacci():
    assert fibonacci(0) == 0
    assert fibonacci(1) == 1
    assert fibonacci(10) == 55
    assert fibonacci(20) == 6765
    import pytest
    with pytest.raises(ValueError):
        fibonacci(-1)
    with pytest.raises(TypeError):
        fibonacci(3.5)
