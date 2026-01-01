from add_one import add_one

def test_add_one():
    assert add_one(1) == 2
    assert add_one(0) == 1
    assert add_one(-1) == 0
    # Edge case: large number
    assert add_one(10**18) == 10**18 + 1
    # Edge case: non-integer raises TypeError
    try:
        add_one('a')
    except TypeError:
        pass
    else:
        raise AssertionError('Expected TypeError')
