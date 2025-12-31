import urllib.request
from typing import Optional

def get_http_status(url: str) -> Optional[int]:
    """Return the HTTP status code for a GET request to *url*.

    Parameters
    ----------
    url : str
        The URL to request.

    Returns
    -------
    Optional[int]
        The HTTP status code if the request succeeds; otherwise ``None``.
    """
    if not url:
        return None
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return response.getcode()
    except Exception:
        return None
