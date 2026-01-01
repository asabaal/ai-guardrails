import pytest
from median import median

def test_median_odd():
    assert median([3, 1, 4]) == 3.0

def test_median_even():
    assert median([3, 1, 4, 2]) == 2.5

def test_median_duplicates():
    assert median([2, 2, 2]) == 2.0

def test_median_single():
    assert median([5]) == 5.0

def test_median_empty():
    with pytest.raises(ValueError):
        median([])
