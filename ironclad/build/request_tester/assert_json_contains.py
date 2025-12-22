from typing import Any


def assert_json_contains(response: Any, key: str, expected_value: Any) -> None:
    """
    Asserts that a JSON-like response contains a given key with an expected value.

    Parameters
    ----------
    response : Any
        An object that implements a ``json()`` method returning the parsed JSON.
    key : str
        The key that must exist in the JSON object.
    expected_value : Any
        The value that the key must have.

    Raises
    ------
    ValueError
        If the response cannot be parsed as JSON.
    AssertionError
        If the parsed JSON is not a dictionary, the key is missing,
        or the value does not match ``expected_value``.
    """
    try:
        data = response.json()
    except Exception as exc:
        raise ValueError("Failed to parse JSON response") from exc

    if not isinstance(data, dict):
        raise AssertionError("JSON response is not an object")

    if key not in data:
        raise AssertionError(f"Key '{key}' not found in JSON response")

    actual_value = data[key]
    if actual_value != expected_value:
        raise AssertionError(
            f"Value for key '{key}' does not match expected value. "
            f"Got {actual_value}, expected {expected_value}"
        )
