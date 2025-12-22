import requests

def request_success(url: str, params: dict | None = None) -> bool:
    """Send a GET request to `url` with optional `params` and assert a 200 status code.

    Returns True if the request succeeds, otherwise raises an AssertionError.
    """
    response = requests.get(url, params=params)
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    return True