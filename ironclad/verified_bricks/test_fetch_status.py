import pytest
import requests
from fetch_status import fetch_status

@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://httpbin.org/status/200", 200),
        ("https://httpbin.org/status/404", 404),
    ],
)
def test_status_codes(url, expected):
    if expected == 404:
        with pytest.raises(requests.exceptions.HTTPError):
            fetch_status(url)
    else:
        assert fetch_status(url) == expected

def test_invalid_url():
    with pytest.raises(requests.exceptions.RequestException):
        fetch_status("ht!tp://invalid-url")
