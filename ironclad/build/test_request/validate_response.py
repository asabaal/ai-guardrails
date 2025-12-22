import re
import requests

def validate_response(response: requests.Response, expected_status: int = 200) -> bool:
    """Validate an HTTP response.

    Parameters
    ----------
    response : requests.Response
        The response object to validate.
    expected_status : int, optional
        The expected HTTP status code (default 200).

    Returns
    -------
    bool
        ``True`` if the response has the expected status code and a
        Content‑Type header that matches the pattern ``application/json``;
        otherwise ``False``.
    """
    if response is None:
        return False
    status = getattr(response, "status_code", None)
    if status != expected_status:
        return False
    headers = getattr(response, "headers", None)
    if not isinstance(headers, dict):
        return False
    # Accept both normal and lowercase header keys.
    content_type = headers.get("Content-Type", headers.get("content-type", ""))
    if not isinstance(content_type, str):
        return False
    # Default pattern is a simple substring match for application/json.
    pattern = r"application/json"
    return re.search(pattern, content_type) is not None
