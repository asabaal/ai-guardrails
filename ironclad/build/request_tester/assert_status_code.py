import requests
from typing import Any

def assert_status_code(response: requests.Response, expected_status: Any) -> None:
    """Assert that the HTTP status code of *response* matches *expected_status*.

    Parameters
    ----------
    response : requests.Response
        The response object to check.
    expected_status : Any
        The status code that the response is expected to have.

    Raises
    ------
    AssertionError
        If ``response.status_code`` does not equal ``expected_status``.
    """
    actual_status = getattr(response, "status_code", None)
    if actual_status != expected_status:
        raise AssertionError(
            f"Expected status {repr(expected_status)} but got {actual_status}."
        )
