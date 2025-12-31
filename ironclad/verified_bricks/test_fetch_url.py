import pytest
import requests
from fetch_url import fetch_url

class MockResponse:
    def __init__(self, status_code=200, text=''):
        self.status_code = status_code
        self.text = text
    def raise_for_status(self):
        if 400 <= self.status_code < 600:
            raise requests.HTTPError(f'Status code: {self.status_code}')

def test_fetch_url_success(monkeypatch):
    def mock_get(url, timeout=5):
        return MockResponse(status_code=200, text='Hello')
    monkeypatch.setattr(requests, 'get', mock_get)
    status, text = fetch_url('http://example.com')
    assert status == 200
    assert text == 'Hello'

def test_fetch_url_http_error(monkeypatch):
    def mock_get(url, timeout=5):
        return MockResponse(status_code=404, text='Not Found')
    monkeypatch.setattr(requests, 'get', mock_get)
    with pytest.raises(requests.HTTPError):
        fetch_url('http://example.com')

def test_fetch_url_timeout(monkeypatch):
    def mock_get(url, timeout=5):
        raise requests.Timeout('Connection timed out')
    monkeypatch.setattr(requests, 'get', mock_get)
    with pytest.raises(requests.Timeout):
        fetch_url('http://example.com')