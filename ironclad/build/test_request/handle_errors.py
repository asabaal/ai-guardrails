import logging
from typing import Any, Dict

# Custom exception to be raised on HTTP errors
class TestRequestError(RuntimeError):
    """Exception raised when an HTTP request returns a client or server error."""

    def __init__(self, status_code: int, headers: Dict[str, Any], body: str) -> None:
        self.status_code = status_code
        self.headers = headers
        self.body = body
        super().__init__(f"HTTP {status_code} error")

    def __repr__(self) -> str:
        return (
            f"TestRequestError(status_code={self.status_code}, "
            f"headers={self.headers!r}, body={self.body!r})"
        )


_logger = logging.getLogger(__name__)


def handle_errors(response: "requests.Response") -> None:
    """Inspect a :class:`requests.Response` for error status codes.

    If the response status code indicates a client error (4xx) or a server error
    (5xx), a detailed error message is logged and a :class:`TestRequestError`
    exception is raised. The exception contains the status code, response
    headers, and response body.

    Parameters
    ----------
    response: requests.Response
        The response object returned by a ``requests`` call.
    """
    status = getattr(response, "status_code", None)
    if status is None:
        _logger.error("Response object has no status_code attribute")
        return
    if status >= 400:
        # Safely extract headers and body; provide defaults if missing
        headers = getattr(response, "headers", {}) or {}
        try:
            body = getattr(response, "text", "") or ""
        except Exception:
            body = "<unable to read body>"
        _logger.error(
            "HTTP error %s received. Headers: %s. Body: %s", status, headers, body
        )
        raise TestRequestError(status, headers, body)
    # For 2xx and 3xx responses, do nothing
