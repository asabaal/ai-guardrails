from merge_sorted_lists import merge_sorted_lists

def test_merge_sorted_lists():
    # Empty lists
    assert merge_sorted_lists([], []) == []
    # One empty list
    assert merge_sorted_lists([1, 3, 5], []) == [1, 3, 5]
    assert merge_sorted_lists([], [2, 4, 6]) == [2, 4, 6]
    # Typical merge
    assert merge_sorted_lists([1, 4, 7], [2, 3, 6]) == [1, 2, 3, 4, 6, 7]
    # Lists with duplicates
    assert merge_sorted_lists([1, 1, 2], [1, 3]) == [1, 1, 1, 2, 3]
    # Negative numbers
    assert merge_sorted_lists([-3, -1, 2], [-2, 0, 3]) == [-3, -2, -1, 0, 2, 3]
    # Same elements
    assert merge_sorted_lists([5, 5, 5], [5, 5]) == [5, 5, 5, 5, 5]
