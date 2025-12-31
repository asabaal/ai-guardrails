import requests


def fetch_json(url: str, timeout: int = 5) -> dict:
    """Fetch JSON data from a given URL.

    Parameters
    ----------
    url : str
        The target URL to send the GET request to. Must start with
        ``http://`` or ``https://``.
    timeout : int, optional
        Timeout for the request in seconds. Default is 5.

    Returns
    -------
    dict
        Parsed JSON response.

    Raises
    ------
    ValueError
        If the URL is empty, does not start with a valid scheme, or the
        response content is not valid JSON.
    RuntimeError
        If the HTTP request fails.
    """
    if not url:
        raise ValueError("URL must not be empty")
    if not url.startswith(("http://", "https://")):
        raise ValueError("URL must start with http:// or https://")

    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"Request failed: {e}") from e

    try:
        return response.json()
    except ValueError as e:
        raise ValueError("Response content is not valid JSON") from e
