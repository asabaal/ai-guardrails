import pytest
from validate_request_line import validate_request_line

@pytest.mark.parametrize("line,expected", [
    ("GET /index.html HTTP/1.1", True),
    ("POST /api/data HTTP/2.0", True),
    ("get /index.html HTTP/1.1", False),
    ("GET index.html HTTP/1.1", False),
    ("GET /index.html HTTP/1", False),
    ("", False),
    ("GET /index.html HTTP/1.1 extra", False),
    ("GET1 /index.html HTTP/1.1", False),
    ("GET /index html HTTP/1.1", False),
    ("GET /index.html HTTP/1.a", False),
    (None, False),
])

def test_validate_request_line(line, expected):
    assert validate_request_line(line) == expected