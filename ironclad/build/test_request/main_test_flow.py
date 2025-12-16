import requests


def send_test_request(url: str, method: str = 'GET', headers: dict = None, payload: dict = None):
    """Send an HTTP request using the requests library.
    Parameters are passed directly to requests.request.
    Raises any exception encountered during the request."""
    try:
        response = requests.request(method=method, url=url, headers=headers, json=payload)
        return response
    except Exception as exc:
        raise


def validate_response(response):
    """Validate that the HTTP response has status code 200.
    Raises ValueError if the status code is not 200."""
    if response.status_code != 200:
        raise ValueError(f"Unexpected status code: {response.status_code}")
    return


def parse_json_payload(response):
    """Parse JSON payload from the response.
    Raises ValueError if parsing fails."""
    try:
        return response.json()
    except Exception as exc:
        raise ValueError("Failed to parse JSON") from exc


def main_test_flow(url: str, method: str = 'GET', headers: dict = None, payload: dict = None) -> dict:
    """Orchestrate the complete test request flow.

    1. Send request using send_test_request.
    2. Validate the response using validate_response.
    3. Parse JSON payload using parse_json_payload.
    4. Return the parsed dictionary.

    Propagates any exception raised during the process to the caller."""
    response = send_test_request(url, method, headers, payload)
    validate_response(response)
    return parse_json_payload(response)
