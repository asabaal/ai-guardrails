import pytest
from make_request import make_request

def test_success(monkeypatch):
    class MockResponse:
        def __init__(self, status_code=200, text='ok'):
            self.status_code = status_code
            self.text = text
    def mock_get(url, timeout=5, headers=None):
        return MockResponse()
    monkeypatch.setattr('requests.get', mock_get)
    result = make_request('https://example.com')
    assert result['status_code'] == 200
    assert result['content'] == 'ok'

def test_timeout(monkeypatch):
    def mock_get(url, timeout=5, headers=None):
        raise requests.exceptions.Timeout
    monkeypatch.setattr('requests.get', mock_get)
    with pytest.raises(TimeoutError, match='timed out'):
        make_request('https://example.com', timeout=1)

def test_request_exception(monkeypatch):
    def mock_get(url, timeout=5, headers=None):
        raise requests.exceptions.HTTPError('Not Found')
    monkeypatch.setattr('requests.get', mock_get)
    with pytest.raises(RuntimeError, match='Request failed'):
        make_request('https://example.com')
