import requests

class HttpError(Exception):
    """Exception raised for HTTP errors.

    Attributes:
        status_code -- HTTP status code returned by the server
        message -- HTTP response text
    """

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"HTTP {status_code}: {message}")


def send_post_request(url: str, data: dict | None = None, json: dict | None = None, timeout: int = 5) -> requests.Response:
    """Send an HTTP POST request.

    Either ``data`` (form‑encoded) or ``json`` may be supplied, but not both.
    Raises:
        ValueError: if both ``data`` and ``json`` are provided.
        HttpError: if the response status code indicates an error (4xx/5xx).
    """
    if data is not None and json is not None:
        raise ValueError("Both 'data' and 'json' parameters cannot be provided simultaneously.")

    try:
        response = requests.post(url, data=data, json=json, timeout=timeout)
    except requests.RequestException as exc:
        # Wrap any low‑level request exception in HttpError for consistency
        raise HttpError(-1, str(exc)) from exc

    if 400 <= response.status_code < 600:
        raise HttpError(response.status_code, response.text)

    return response
