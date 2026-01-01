from clamp import clamp

def test_clamp():
    # Normal case
    assert clamp(5, 1, 10) == 5
    # Below min
    assert clamp(-3, 0, 5) == 0
    # Above max
    assert clamp(12, 0, 10) == 10
    # min > max should be swapped
    assert clamp(7, 10, 3) == 7
    # Edge case: value equals min
    assert clamp(0, 0, 5) == 0
    # Edge case: value equals max
    assert clamp(5, 0, 5) == 5
    # Edge case: all equal
    assert clamp(3, 3, 3) == 3
    # Edge case: negative bounds
    assert clamp(-2, -5, -1) == -2
    # Edge case: value outside negative bounds
    assert clamp(-10, -5, -1) == -5
    # Edge case: min greater than max and value outside
    assert clamp(-10, 5, -5) == -5
