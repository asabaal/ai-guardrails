def test_add_numbers():
    from add_numbers import add_numbers
    assert add_numbers(1, 2) == 3
    assert add_numbers(-1, 5) == 4
    assert add_numbers(0.5, 0.5) == 1.0
    import pytest
    with pytest.raises(TypeError):
        add_numbers('1', 2)
    with pytest.raises(TypeError):
        add_numbers(1, None)
