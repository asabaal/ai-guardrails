import argparse
from typing import List


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Convert temperature.')
    parser.add_argument('-v', '--value', type=float, required=True, help='Numeric value to convert.')
    parser.add_argument('-u', '--unit', choices=['c', 'f'], required=True, help='Source unit (c or f).')
    parser.add_argument('-t', '--target', choices=['c', 'f'], required=True, help='Target unit (c or f).')
    args = parser.parse_args(argv)
    if args.unit == args.target:
        parser.error('Target unit must be the opposite of source unit.')
    return args
