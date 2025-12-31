import pytest
from process_request import process_request

def test_valid_request():
    req = {"method": "GET", "path": "/api", "params": {"b": 2, "a": 1}}
    method, path, sorted_params = process_request(req)
    assert method == "GET"
    assert path == "/api"
    assert sorted_params == [("a", 1), ("b", 2)]

def test_no_params():
    req = {"method": "POST", "path": "/submit"}
    method, path, sorted_params = process_request(req)
    assert method == "POST"
    assert path == "/submit"
    assert sorted_params == []

def test_missing_method():
    req = {"path": "/test"}
    with pytest.raises(ValueError) as exc:
        process_request(req)
    assert "Missing required keys" in str(exc.value)

def test_wrong_type_method():
    req = {"method": 123, "path": "/test"}
    with pytest.raises(TypeError):
        process_request(req)

def test_params_nonstring_keys():
    req = {"method": "GET", "path": "/", "params": {"1": "one"}}
    method, path, sorted_params = process_request(req)
    assert sorted_params == [("1", "one")]

def test_params_nonstring_key_type():
    req = {"method": "GET", "path": "/", "params": {1: "one"}}
    with pytest.raises(TypeError):
        process_request(req)

def test_request_not_dict():
    with pytest.raises(TypeError):
        process_request(["method", "GET", "path", "/"])

def test_empty_strings():
    req = {"method": "", "path": ""}
    method, path, sorted_params = process_request(req)
    assert method == ""
    assert path == ""
    assert sorted_params == []