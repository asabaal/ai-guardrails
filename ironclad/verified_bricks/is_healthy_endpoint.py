import requests

def is_healthy_endpoint(url: str, timeout: float = 5.0) -> bool:
    '''Return True if a GET request to the given URL returns status code 200.
    
    Parameters
    ----------
    url : str
        The URL to check.
    timeout : float, optional
        The timeout for the request in seconds. Defaults to 5.0.
    
    Returns
    -------
    bool
        True if status code is 200, False otherwise.
    '''
    if not isinstance(url, str) or not url:
        return False
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except (requests.RequestException, Exception):
        return False