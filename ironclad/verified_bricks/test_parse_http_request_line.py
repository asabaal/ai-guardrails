import pytest
from parse_http_request_line import parse_http_request_line

def test_valid_request_line():
    result = parse_http_request_line("GET /index.html HTTP/1.1")
    assert result == {"method": "GET", "path": "/index.html", "version": "HTTP/1.1"}

def test_method_case_insensitivity():
    result = parse_http_request_line("post /submit HTTP/1.0")
    assert result == {"method": "POST", "path": "/submit", "version": "HTTP/1.0"}

def test_invalid_method():
    with pytest.raises(ValueError):
        parse_http_request_line("FOO /path HTTP/1.1")

def test_missing_parts():
    with pytest.raises(ValueError):
        parse_http_request_line("GET /only")

def test_invalid_path():
    with pytest.raises(ValueError):
        parse_http_request_line("GET index.html HTTP/1.1")

def test_invalid_version():
    with pytest.raises(ValueError):
        parse_http_request_line("GET / HTTP/3.0")

def test_non_string_input():
    with pytest.raises(ValueError):
        parse_http_request_line(123)
