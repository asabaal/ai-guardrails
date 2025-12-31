import pytest
from is_healthy import is_healthy
import requests

def test_valid_url(monkeypatch):
    class DummyResponse:
        status_code = 200
    def mock_get(*args, **kwargs):
        return DummyResponse()
    monkeypatch.setattr(requests, 'get', mock_get)
    assert is_healthy('http://example.com') is True

def test_non_200_url(monkeypatch):
    class DummyResponse:
        status_code = 404
    def mock_get(*args, **kwargs):
        return DummyResponse()
    monkeypatch.setattr(requests, 'get', mock_get)
    assert is_healthy('http://example.com') is False

def test_request_exception(monkeypatch):
    def mock_get(*args, **kwargs):
        raise requests.ConnectionError
    monkeypatch.setattr(requests, 'get', mock_get)
    assert is_healthy('http://example.com') is False

def test_empty_url():
    assert is_healthy('') is False