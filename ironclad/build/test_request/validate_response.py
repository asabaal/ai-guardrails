import logging
import requests

def validate_response(response: requests.Response) -> bool:
    """Validate an HTTP response.

    Parameters
    ----------
    response : requests.Response
        The HTTP response to validate.

    Returns
    -------
    bool
        ``True`` if the status code indicates success (200–299).

    Raises
    ------
    requests.HTTPError
        If the status code indicates a failure. The error message contains the
        status code and reason phrase.

    Notes
    -----
    A warning is logged when the status code is 429 (rate limiting) or any
    5xx server error.
    """
    status = response.status_code
    # Log warnings for rate limiting or server errors
    if status == 429 or 500 <= status <= 599:
        logging.warning(f"Received status code {status}: {response.reason}")
    # Success range
    if 200 <= status <= 299:
        return True
    # Failure: raise HTTPError with message
    raise requests.HTTPError(f"Status {status}: {response.reason}")