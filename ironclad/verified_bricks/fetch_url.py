import requests

def fetch_url(url, timeout=5):
    """Fetch URL and return status code and text. Raises requests.RequestException on failure."""
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.status_code, response.text