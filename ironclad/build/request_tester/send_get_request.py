import requests
from typing import Dict, Optional

class RequestError(Exception):
    """Custom exception raised when a network error occurs during a GET request."""
    def __init__(self, message: str) -> None:
        super().__init__(message)


def function_name(url: str, params: Optional[Dict] = None, timeout: int = 5) -> requests.Response:
    """Send an HTTP GET request to ``url`` with optional ``params`` and ``timeout``.

    Args:
        url: The target URL.
        params: Optional dictionary of query parameters.
        timeout: Timeout in seconds for the request.

    Returns:
        The raw :class:`requests.Response` object.

    Raises:
        RequestError: If a network error occurs.
    """
    try:
        response = requests.get(url, params=params, timeout=timeout)
        return response
    except requests.exceptions.RequestException as exc:
        raise RequestError(f"Network error occurred while requesting {url}: {exc}") from exc
