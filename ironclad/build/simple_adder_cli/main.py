import sys
from parse_args import parse_args
from convert_to_float import convert_to_float
from add_numbers import add_numbers
from print_result import print_result


def main():
    try:
        arg1, arg2 = parse_args()
    except Exception as e:
        print(f"Error parsing arguments: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        num1 = convert_to_float(arg1)
        num2 = convert_to_float(arg2)
    except ValueError as e:
        print(f"Invalid number: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        result = add_numbers(num1, num2)
    except Exception as e:
        print(f"Error adding numbers: {e}", file=sys.stderr)
        sys.exit(1)

    print_result(result)


if __name__ == "__main__":
    main()
