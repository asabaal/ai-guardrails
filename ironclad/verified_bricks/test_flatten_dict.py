import pytest
from flatten_dict import flatten_dict

@pytest.mark.parametrize(
    "input_dict,expected",
    [
        ({}, {}),
        ({'a': 1, 'b': 2}, {'a': 1, 'b': 2}),
        ({'a': {'b': 2}}, {'a.b': 2}),
        ({'a': {'b': {'c': 3}}}, {'a.b.c': 3}),
        ({'a': {}, 'b': {'c': 4}}, {'a': {}, 'b.c': 4}),
        ({'x': {'y': None}}, {'x.y': None}),
    ],
)
def test_flatten_dict(input_dict, expected):
    assert flatten_dict(input_dict) == expected

# Edge case: non-dict values should be returned as is

def test_non_dict_value():
    assert flatten_dict({'a': 1}) == {'a': 1}

# Edge case: key with separator already present

def test_existing_separator():
    assert flatten_dict({'a.b': 1}) == {'a.b': 1}
