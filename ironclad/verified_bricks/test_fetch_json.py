import pytest
import requests
from unittest.mock import patch, MagicMock
from fetch_json import fetch_json


@patch('requests.get')
def test_fetch_json_success(mock_get):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {'key': 'value'}
    mock_get.return_value = mock_response

    result = fetch_json('https://example.com')
    assert result == {'key': 'value'}


@patch('requests.get')
def test_fetch_json_invalid_url(mock_get):
    with pytest.raises(ValueError):
        fetch_json('ftp://example.com')


@patch('requests.get')
def test_fetch_json_request_exception(mock_get):
    mock_get.side_effect = requests.exceptions.Timeout('timeout')
    with pytest.raises(RuntimeError):
        fetch_json('https://example.com')


@patch('requests.get')
def test_fetch_json_invalid_json(mock_get):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.side_effect = ValueError('invalid JSON')
    mock_get.return_value = mock_response
    with pytest.raises(ValueError):
        fetch_json('https://example.com')
