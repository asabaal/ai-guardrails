import pytest
from convert_list_to_dict_by_id import list_to_dict_by_id

def test_normal():
    items = [{'id': 1, 'name': 'a'}, {'id': 2, 'name': 'b'}]
    assert list_to_dict_by_id(items) == {
        1: {'id': 1, 'name': 'a'},
        2: {'id': 2, 'name': 'b'}
    }

def test_duplicate_ids():
    items = [{'id': 1, 'name': 'a'}, {'id': 1, 'name': 'b'}]
    assert list_to_dict_by_id(items) == {1: {'id': 1, 'name': 'b'}}

def test_missing_id():
    items = [{'name': 'a'}, {'id': 2, 'name': 'b'}]
    assert list_to_dict_by_id(items) == {2: {'id': 2, 'name': 'b'}}

def test_empty_list():
    assert list_to_dict_by_id([]) == {}

def test_non_list_raises():
    with pytest.raises(TypeError):
        list_to_dict_by_id(None)
