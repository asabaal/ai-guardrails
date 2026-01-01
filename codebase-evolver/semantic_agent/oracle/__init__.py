"""
Oracle Layer - Pyright LSP Integration

This module provides a deterministic semantic oracle for Python codebases
by running Pyright as a daemon and querying it via JSON-RPC.
"""

from .pyright_daemon import (
    start_daemon,
    stop_daemon,
    initialize,
    get_definition,
    get_references,
    get_type_info,
)

__all__ = [
    "start_daemon",
    "stop_daemon",
    "initialize",
    "get_definition",
    "get_references",
    "get_type_info",
]
