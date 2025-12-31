import argparse
from typing import List


def parse_args(argv: List[str]) -> argparse.Namespace:
    """Parse command-line arguments.

    Expects one of the mutually exclusive flags:
        -c / --celsius  for Celsius input
        -f / --fahrenheit for Fahrenheit input
    Requires a positional temperature value.

    Returns:
        argparse.Namespace with 'celsius' or 'fahrenheit' attribute set to True when the flag is provided, otherwise None.
    """
    parser = argparse.ArgumentParser(description='Temperature parser')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c', '--celsius', dest='celsius', action='store_true', default=None,
                       help='Input temperature in Celsius')
    group.add_argument('-f', '--fahrenheit', dest='fahrenheit', action='store_true', default=None,
                       help='Input temperature in Fahrenheit')
    parser.add_argument('temperature', help='Temperature value as a string')
    return parser.parse_args(argv)
