def is_healthy(url: str) -> bool:
    import requests
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except (requests.RequestException, Exception):
        return False