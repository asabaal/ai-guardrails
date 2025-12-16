import requests
from typing import Dict

ALLOWED_METHODS = {"GET", "POST", "PUT", "DELETE", "PATCH"}

def send_test_request(url: str, method: str = "GET", headers: Dict[str, str] = None, payload: Dict = None) -> requests.Response:
    """Send an HTTP request using the requests library.

    Parameters
    ----------
    url : str
        Target URL.
    method : str, optional
        HTTP method. Must be one of 'GET', 'POST', 'PUT', 'DELETE', or 'PATCH'. Default is 'GET'.
    headers : dict, optional
        Dictionary of HTTP headers.
    payload : dict, optional
        JSON payload to send in the body of the request.

    Returns
    -------
    requests.Response
        The raw response object.

    Raises
    ------
    ValueError
        If *method* is not one of the allowed HTTP verbs.
    """
    method = method.upper()
    if method not in ALLOWED_METHODS:
        raise ValueError(f"Unsupported HTTP method: {method}. Allowed methods are: {', '.join(sorted(ALLOWED_METHODS))}")

    response = requests.request(
        method=method,
        url=url,
        headers=headers,
        json=payload,
        timeout=10,
    )
    return response