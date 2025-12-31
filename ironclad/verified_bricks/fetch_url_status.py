def fetch_url_status(url, timeout=5):
    import requests
    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        return resp.status_code
    except requests.exceptions.RequestException as e:
        raise e