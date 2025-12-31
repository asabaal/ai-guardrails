import pytest
import requests
from fetch_url_status import fetch_url_status
from unittest.mock import patch, Mock


def test_fetch_url_status_success():
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status.return_value = None
    with patch('requests.get', return_value=mock_resp):
        assert fetch_url_status('http://example.com') == 200


def test_fetch_url_status_http_error():
    mock_resp = Mock()
    mock_resp.status_code = 404
    mock_resp.raise_for_status.side_effect = requests.exceptions.HTTPError()
    with patch('requests.get', return_value=mock_resp):
        with pytest.raises(requests.exceptions.HTTPError):
            fetch_url_status('http://example.com')


def test_fetch_url_status_connection_error():
    with patch('requests.get', side_effect=requests.exceptions.ConnectionError()):
        with pytest.raises(requests.exceptions.ConnectionError):
            fetch_url_status('http://example.com')


def test_fetch_url_status_invalid_url():
    with pytest.raises(requests.exceptions.RequestException):
        fetch_url_status(None)
