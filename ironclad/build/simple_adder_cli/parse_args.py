import argparse


def parse_args() -> argparse.Namespace:
    """Parse two positional numeric arguments.

    Returns:
        argparse.Namespace: Contains ``num1`` and ``num2`` as integers.

    Raises:
        SystemExit: If the number of arguments is incorrect or if the
        arguments cannot be parsed as integers.
    """
    parser = argparse.ArgumentParser(
        description="Add two numbers",
        usage="%(prog)s NUM1 NUM2",
    )
    parser.add_argument("num1", type=int, help="First number")
    parser.add_argument("num2", type=int, help="Second number")
    return parser.parse_args()
