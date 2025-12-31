import pytest
from validate_request import validate_request


def test_valid_request():
    req = {
        'method': 'GET',
        'url': 'https://example.com/api',
        'headers': {'Accept': 'application/json'},
        'body': None
    }
    assert validate_request(req)


def test_missing_method():
    req = {
        'url': 'https://example.com/api'
    }
    assert not validate_request(req)


def test_invalid_method():
    req = {
        'method': 'FETCH',
        'url': 'https://example.com/api'
    }
    assert not validate_request(req)


def test_invalid_url():
    req = {
        'method': 'GET',
        'url': 'ftp://example.com'
    }
    assert not validate_request(req)


def test_non_dict_headers():
    req = {
        'method': 'GET',
        'url': 'https://example.com/api',
        'headers': ['Accept']
    }
    assert not validate_request(req)


def test_headers_with_non_string():
    req = {
        'method': 'GET',
        'url': 'https://example.com/api',
        'headers': {'Accept': 123}
    }
    assert not validate_request(req)


def test_body_with_invalid_type():
    req = {
        'method': 'POST',
        'url': 'https://example.com/api',
        'body': 42
    }
    assert not validate_request(req)


def test_missing_url():
    req = {
        'method': 'GET'
    }
    assert not validate_request(req)


def test_empty_request():
    assert not validate_request({})