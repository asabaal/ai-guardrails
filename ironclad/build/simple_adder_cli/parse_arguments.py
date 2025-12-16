import argparse
from typing import List, Tuple


def parse_arguments(argv: List[str]) -> Tuple[int, int]:
    def to_int(value: str) -> int:
        try:
            return int(value)
        except ValueError as e:
            raise argparse.ArgumentTypeError(f"'{value}' is not a valid integer") from e

    parser = argparse.ArgumentParser(description='Parse two integer operands')
    parser.add_argument('num1', type=to_int, help='First integer')
    parser.add_argument('num2', type=to_int, help='Second integer')

    args = parser.parse_args(argv)
    return args.num1, args.num2
