import typing
from typing import List, Tuple


def parse_arguments(argv: List[str]) -> Tuple[str, str]:
    """Parse command‑line arguments.

    Args:
        argv: List of command line arguments.

    Returns:
        A tuple containing the first two positional arguments.

    Raises:
        ValueError: If the number of arguments is not exactly two.
    """
    if len(argv) != 2:
        raise ValueError(f"Expected exactly two arguments, got {len(argv)}: {argv}")
    return tuple(argv)  # type: ignore[return-value]
