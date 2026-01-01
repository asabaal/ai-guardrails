from nth_fibonacci import nth_fibonacci

def test_nth_fibonacci():
    # Basic sanity checks
    assert nth_fibonacci(0) == 0
    assert nth_fibonacci(1) == 1
    assert nth_fibonacci(2) == 1
    assert nth_fibonacci(3) == 2
    assert nth_fibonacci(10) == 55
    # Large index
    assert nth_fibonacci(50) == 12586269025
    # Edge case: very large index, still returns correctly
    assert nth_fibonacci(100) == 354224848179261915075
    # Type and value error checks
    try:
        nth_fibonacci("10")
    except TypeError:
        pass
    else:
        raise AssertionError("Expected TypeError for non‑int input")
    try:
        nth_fibonacci(-5)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for negative input")
