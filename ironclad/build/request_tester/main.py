import argparse
import sys
import importlib
from typing import Callable, Any


def _load_callable(module_name: str, *candidate_names: str) -> Callable[..., Any]:
    """
    Dynamically load a callable from a module.  Tries the provided candidate names
    in order; if none match, returns the first callable found in the module.
    Raises ImportError if no suitable callable can be found.
    """
    module = importlib.import_module(module_name)
    for name in candidate_names:
        func = getattr(module, name, None)
        if callable(func):
            return func
    # Fallback: pick the first callable in the module
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if callable(attr):
            return attr
    raise ImportError(f"Unable to find a callable in module '{module_name}'.")


# Lazy load the utilities.  The names may differ between implementations,
# so we try several plausible candidates for each.
try:
    send_get_request = _load_callable(
        "send_get_request", "send_get_request", "send_get", "make_get_request"
    )
except ImportError as exc:
    print(f"Error loading GET helper: {exc}", file=sys.stderr)
    send_get_request = None

try:
    send_post_request = _load_callable(
        "send_post_request", "send_post_request", "send_post", "make_post_request"
    )
except ImportError as exc:
    print(f"Error loading POST helper: {exc}", file=sys.stderr)
    send_post_request = None

try:
    assert_status_code = _load_callable(
        "assert_status_code", "assert_status_code", "check_status_code"
    )
except ImportError as exc:
    print(f"Error loading status-code assertion: {exc}", file=sys.stderr)
    assert_status_code = None

try:
    assert_json_contains = _load_callable(
        "assert_json_contains", "assert_json_contains", "check_json_contains"
    )
except ImportError as exc:
    print(f"Error loading JSON assertion: {exc}", file=sys.stderr)
    assert_json_contains = None

try:
    test_request_success = _load_callable(
        "test_request_success", "test_request_success", "run_tests"
    )
except ImportError as exc:
    print(f"Error loading bundled test helper: {exc}", file=sys.stderr)
    test_request_success = None


def _ensure_callable(name: str, func: Callable[..., Any]) -> Callable[..., Any]:
    if func is None:
        raise RuntimeError(f"Required function '{name}' could not be loaded.")
    return func


def main() -> None:
    """
    Demo entry point that exercises the request utilities.

    The script can be used manually to test a live endpoint or as a
    lightweight CLI for quick checks.  The helper functions that are
    normally consumed by pytest are also imported here so that the module
    can be executed as a stand‑alone script.
    """
    parser = argparse.ArgumentParser(
        description="Demo of request utilities – perform a GET/POST and run basic assertions."
    )
    parser.add_argument(
        "--url",
        required=True,
        help="Target URL to send the request to.",
    )
    parser.add_argument(
        "--method",
        choices=["GET", "POST"],
        default="GET",
        help="HTTP method to use for the request (default: GET).",
    )
    parser.add_argument(
        "--status",
        type=int,
        help="Expected HTTP status code; an assertion will be performed if provided.",
    )
    parser.add_argument(
        "--json-key",
        help="JSON key that must be present in the response body.",
    )
    parser.add_argument(
        "--json-value",
        help="Expected value for the JSON key; used only if --json-key is set.",
    )
    parser.add_argument(
        "--run-tests",
        action="store_true",
        help="If set, the bundled test_request_success helper will be executed.",
    )

    args = parser.parse_args()

    try:
        # Ensure we have the required helpers
        get_func = _ensure_callable("send_get_request", send_get_request)
        post_func = _ensure_callable("send_post_request", send_post_request)
        status_assert = _ensure_callable("assert_status_code", assert_status_code)
        json_assert = _ensure_callable("assert_json_contains", assert_json_contains)

        if args.method == "GET":
            response = get_func(args.url)
        else:
            # For a POST we send an empty payload – callers can extend this.
            response = post_func(args.url, data={})

        print(f"Response status: {response.status_code}")

        if args.status is not None:
            status_assert(response, args.status)
            print(f"Status code assertion passed: {response.status_code}")

        if args.json_key:
            if args.json_value is None:
                raise ValueError("--json-value must be supplied when --json-key is used.")
            json_assert(response, args.json_key, args.json_value)
            print(
                f"JSON contains assertion passed for key '{args.json_key}' with value '{args.json_value}'"
            )

        if args.run_tests:
            if test_request_success is None:
                raise RuntimeError("Bundled test helper 'test_request_success' could not be loaded.")
            test_request_success()
            print("test_request_success() executed successfully.")

        print("All assertions passed.")

    except AssertionError as err:
        print(f"Assertion failed: {err}")
        sys.exit(1)
    except Exception as exc:
        print(f"An error occurred: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()