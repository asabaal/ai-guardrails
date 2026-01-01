import pytest
from split_list_by_separator import split_list_by_separator

def test_split_list_by_separator():
    assert split_list_by_separator([], 0) == []
    assert split_list_by_separator([1, 2, 3], 0) == [[1, 2, 3]]
    assert split_list_by_separator([1, 0, 2, 0, 3], 0) == [[1], [2], [3]]
    assert split_list_by_separator([0, 1, 2, 3], 0) == [[], [1, 2, 3]]
    assert split_list_by_separator([1, 2, 3, 0], 0) == [[1, 2, 3], []]
    assert split_list_by_separator([1, 0, 0, 2], 0) == [[1], [], [2]]
    assert split_list_by_separator([1, 2, 3], None) == [[1, 2, 3]]
    assert split_list_by_separator([None, 1, None, 2], None) == [[None, 1, None, 2]]
