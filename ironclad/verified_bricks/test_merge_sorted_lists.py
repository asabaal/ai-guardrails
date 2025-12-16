import pytest
from merge_sorted_lists import merge_sorted_lists

def test_both_empty():
    assert merge_sorted_lists([], []) == []

def test_one_empty():
    assert merge_sorted_lists([1, 2, 3], []) == [1, 2, 3]
    assert merge_sorted_lists([], [-1, 0, 1]) == [-1, 0, 1]

def test_normal():
    assert merge_sorted_lists([1, 3, 5], [2, 4, 6]) == [1, 2, 3, 4, 5, 6]

def test_duplicates():
    assert merge_sorted_lists([1, 2, 2, 3], [2, 2, 4]) == [1, 2, 2, 2, 2, 3, 4]

def test_negative():
    assert merge_sorted_lists([-5, -3, -1], [0, 1, 2]) == [-5, -3, -1, 0, 1, 2]
    assert merge_sorted_lists([-3, -2], [-4, 0]) == [-4, -3, -2, 0]

def test_large():
    import random
    a = sorted(random.sample(range(1000), 500))
    b = sorted(random.sample(range(1000, 2000), 500))
    expected = sorted(a + b)
    assert merge_sorted_lists(a, b) == expected
