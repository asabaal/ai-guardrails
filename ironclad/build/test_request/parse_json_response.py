import requests

def parse_json_response(response: requests.Response) -> dict:
    """Parse a :class:`requests.Response` object and return a dictionary.

    Parameters
    ----------
    response:
        The :class:`requests.Response` to parse.

    Returns
    -------
    dict
        The parsed JSON object.

    Raises
    ------
    ValueError
        If the response body is not valid JSON.
    TypeError
        If the parsed JSON is not a dictionary.
    """
    try:
        data = response.json()
    except ValueError as exc:
        # requests.json() raises ValueError (or a subclass) on parse errors
        raise ValueError("Invalid JSON") from exc
    if not isinstance(data, dict):
        raise TypeError("JSON is not a dictionary")
    return data
