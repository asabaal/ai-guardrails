#!/usr/bin/env python3
"""
Main entry point for the test request pipeline.

This module imports the public functions from the local package and exposes a
command‑line interface that forwards parameters to ``main_test_flow``.

The logic is as follows:

1. Import the required symbols from the sibling modules.
2. Parse command‑line arguments and fall back to environment variables if a
   value is not supplied on the command line.
3. Call ``main_test_flow`` with the collected arguments.
4. Handle ``TestRequestError`` (defined in ``handle_errors``) and display a
   user‑friendly error message.
5. Expose a ``__main__`` guard so the module can be executed as a script or
   imported by tests.

The command‑line options are intentionally lightweight: only ``--url`` and
``--payload`` are supported, because the actual signature of ``main_test_flow``
is not known.  If the target function requires additional keyword arguments
they can be added to the ``argparse`` configuration and forwarded to the
call.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

# Import public functions from sibling modules.  Each file defines a single
# function with the same name as the module.  If the import fails we surface
# an informative error.
try:
    from send_test_request import send_test_request
    from validate_response import validate_response
    from parse_json_response import parse_json_response
    from handle_errors import handle_errors, TestRequestError
    from main_test_flow import main_test_flow
except Exception as exc:  # pragma: no cover - import-time failure
    sys.stderr.write(
        f"Failed to import required modules: {exc}\n"
    )
    sys.exit(1)


def _build_argument_parser() -> argparse.ArgumentParser:
    """Create an argument parser for the script.

    The parser supports the following options:

    ``--url``
        Target URL for the test request.  Defaults to the ``URL`` environment
        variable.
    ``--payload``
        JSON string payload to send with the request.  Defaults to the
        ``PAYLOAD`` environment variable.

    Additional arguments can be added later if the ``main_test_flow``
    signature expands.
    """
    parser = argparse.ArgumentParser(
        description="Run the test request flow with optional URL and payload."
    )
    parser.add_argument(
        "--url",
        default=os.getenv("URL"),
        help="Target URL for the test request (env: URL)",
    )
    parser.add_argument(
        "--payload",
        default=os.getenv("PAYLOAD"),
        help="JSON payload for the request (env: PAYLOAD)",
    )
    return parser


def _parse_payload(raw: str | None) -> any:
    """Safely parse a JSON payload.

    If the supplied string is ``None`` or empty, ``None`` is returned.
    On JSON decoding errors an informative exception is raised.
    """
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:  # pragma: no cover
        raise ValueError(f"Invalid JSON payload: {exc}") from exc


def main() -> None:
    """Entry point executed when the module is run as a script.

    The function collects arguments, forwards them to ``main_test_flow`` and
    handles ``TestRequestError`` with a friendly message.
    """
    parser = _build_argument_parser()
    args = parser.parse_args()

    # Prepare arguments for the flow.  ``main_test_flow`` is expected to
    # accept keyword arguments; we construct a dictionary that can be expanded
    # easily.
    flow_kwargs: dict[str, any] = {
        "url": args.url,
        "payload": _parse_payload(args.payload),
    }

    try:
        main_test_flow(**flow_kwargs)
    except TestRequestError as err:  # pragma: no cover - exercised in tests
        # Print a user‑friendly error message and exit with a non‑zero status.
        print(f"Test request failed: {err}", file=sys.stderr)
        sys.exit(1)
    except Exception as err:  # pragma: no cover - unforeseen errors
        # Catch-all for unexpected errors to prevent stack traces from leaking
        # to end users.
        print(f"An unexpected error occurred: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover - runtime guard
    main()
