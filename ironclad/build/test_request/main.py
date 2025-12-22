#!/usr/bin/env python3
"""
Main script to test HTTP endpoints using the send_request and validate_response helpers.

The script supports optional command‑line arguments to override the default list of URLs
and the expected HTTP status code. It prints a summary of the test results.
"""

import argparse
import sys
from typing import List, Dict, Any

# Import component functions
from send_request import send_request
from validate_response import validate_response


def parse_arguments() -> argparse.Namespace:
    """Parse command‑line arguments.

    Returns:
        argparse.Namespace: Parsed arguments with attributes 'urls' (List[str])
        and 'status' (int).
    """
    parser = argparse.ArgumentParser(description="Test HTTP endpoints.")
    parser.add_argument(
        "--urls",
        type=str,
        help="Comma‑separated list of URLs to test. Overrides the defaults.",
    )
    parser.add_argument(
        "--status",
        type=int,
        help="Expected HTTP status code for all responses. Defaults to 200.",
    )
    return parser.parse_args()


def main() -> None:
    """Entry point for the test runner."""
    args = parse_arguments()

    # Default configuration
    default_urls = [
        "https://example.com",
        "https://httpbin.org/status/200",
        "https://httpbin.org/status/404",
    ]
    expected_status = 200

    # Override with command‑line arguments if provided
    if args.urls:
        urls: List[str] = [u.strip() for u in args.urls.split(",") if u.strip()]
        if not urls:
            print("Error: --urls provided but no valid URLs were parsed.", file=sys.stderr)
            sys.exit(1)
    else:
        urls = default_urls

    if args.status is not None:
        expected_status = args.status

    results: List[Dict[str, Any]] = []

    for url in urls:
        try:
            response = send_request(url)
        except Exception as exc:
            # Capture request errors
            results.append({
                "url": url,
                "error": f"Request failed: {exc}",
            })
            print(f"{url} -> Request failed: {exc}")
            continue

        try:
            is_valid = validate_response(response, expected_status)
        except Exception as exc:
            # Capture validation errors
            results.append({
                "url": url,
                "status": response.status_code,
                "error": f"Validation raised: {exc}",
            })
            print(f"{url} -> Validation raised: {exc}")
            continue

        results.append({
            "url": url,
            "status": response.status_code,
            "valid": is_valid,
        })
        status_msg = "PASS" if is_valid else "FAIL"
        print(f"{url} -> status {response.status_code} [{status_msg}]")

    # Summary
    total = len(urls)
    successes = sum(1 for r in results if r.get("valid", False))
    failures = total - successes

    print("\nTest Summary:\n")
    print(f"Total URLs tested: {total}")
    print(f"Successful validations: {successes}")
    print(f"Failed validations: {failures}")


if __name__ == "__main__":
    main()
