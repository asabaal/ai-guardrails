import pytest
from group_words_by_length import group_words_by_length

def test_basic():
    words = ["a", "bb", "ccc", "d", "ee"]
    expected = {1: ["a", "d"], 2: ["bb", "ee"], 3: ["ccc"]}
    assert group_words_by_length(words) == expected

def test_empty():
    assert group_words_by_length([]) == {}

def test_duplicates():
    words = ["cat", "dog", "bat"]
    expected = {3: ["cat", "dog", "bat"]}
    assert group_words_by_length(words) == expected

def test_non_string():
    with pytest.raises(TypeError):
        group_words_by_length([1, "a"])

def test_preserve_order():
    words = ["ab", "cd", "a", "b"]
    expected = {2: ["ab", "cd"], 1: ["a", "b"]}
    assert group_words_by_length(words) == expected