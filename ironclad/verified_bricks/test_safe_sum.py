import pytest
from safe_sum import safe_sum

def test_safe_sum():
    assert safe_sum([1, 2, 3]) == 6
    assert safe_sum([1.5, 2.5]) == 4.0
    assert safe_sum([]) == 0
    assert safe_sum([], default=10) == 10
    assert safe_sum((1, 2, 3)) == 6
    assert safe_sum([1, -2, 3]) == 2
    with pytest.raises(TypeError):
        safe_sum('not a list')
    with pytest.raises(TypeError):
        safe_sum([1, 'a', 3])
