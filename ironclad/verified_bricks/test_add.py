def test_add():
    from add import add
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0
    # Edge cases
    assert add(1.5, 2.5) == 4.0
    assert add(-10, -5) == -15
