import pytest
from is_healthy_endpoint import is_healthy_endpoint

class DummyResponse:
    def __init__(self, status_code):
        self.status_code = status_code

def test_successful_request(monkeypatch):
    def mock_get(url, timeout=5.0):
        return DummyResponse(200)
    monkeypatch.setattr('requests.get', mock_get)
    assert is_healthy_endpoint('http://example.com') is True

def test_non_200_status(monkeypatch):
    def mock_get(url, timeout=5.0):
        return DummyResponse(404)
    monkeypatch.setattr('requests.get', mock_get)
    assert is_healthy_endpoint('http://example.com') is False

def test_timeout_exception(monkeypatch):
    def mock_get(url, timeout=5.0):
        raise requests.Timeout()
    monkeypatch.setattr('requests.get', mock_get)
    assert is_healthy_endpoint('http://example.com') is False

def test_connection_error_exception(monkeypatch):
    def mock_get(url, timeout=5.0):
        raise requests.ConnectionError()
    monkeypatch.setattr('requests.get', mock_get)
    assert is_healthy_endpoint('http://example.com') is False

def test_invalid_url_none():
    assert is_healthy_endpoint(None) is False

def test_invalid_url_empty():
    assert is_healthy_endpoint('') is False

def test_invalid_url_non_string():
    assert is_healthy_endpoint(123) is False

def test_custom_timeout_passed(monkeypatch):
    captured = {}
    def mock_get(url, timeout=5.0):
        captured['timeout'] = timeout
        return DummyResponse(200)
    monkeypatch.setattr('requests.get', mock_get)
    assert is_healthy_endpoint('http://example.com', timeout=2.0) is True
    assert captured['timeout'] == 2.0