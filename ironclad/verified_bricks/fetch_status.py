import requests

def fetch_status(url: str, timeout: float = 5.0) -> int:
    """Send GET request and return status code.
    Raises requests.exceptions.RequestException on error."""
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.status_code
