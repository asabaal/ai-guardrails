import requests
import builtins

# Ensure requests is available to test's globals via builtins
if not hasattr(builtins, 'requests'):
    builtins.requests = requests

def make_request(url, timeout=5, headers=None):
    try:
        response = requests.get(url, timeout=timeout, headers=headers)
        return {
            'status_code': response.status_code,
            'content': response.text,
        }
    except requests.exceptions.Timeout:
        raise TimeoutError(f'Request timed out after {timeout} seconds')
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f'Request failed: {e}')