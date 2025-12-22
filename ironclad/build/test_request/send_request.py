import requests
from typing import Dict, Optional

class RequestError(Exception):
    """Custom exception raised when an HTTP request fails."""
    def __init__(self, message: str, response: Optional[requests.Response] = None):
        super().__init__(message)
        self.response = response


def send_request(url: str, headers: Dict = None, timeout: int = 10) -> requests.Response:
    """Send an HTTP GET request.

    Parameters:
        url (str): Target URL.
        headers (dict, optional): HTTP headers.
        timeout (int, optional): Timeout in seconds.

    Returns:
        requests.Response: The response object.

    Raises:
        RequestError: If the request fails due to connection issues,
            timeouts, or non‑2xx status codes. The response (if any) is
            attached to the exception for inspection.
    """
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
    except requests.exceptions.RequestException as exc:
        raise RequestError(f"Request failed: {exc}") from exc
    if not 200 <= response.status_code < 300:
        raise RequestError(f"Non‑2xx status code: {response.status_code}", response=response)
    return response
