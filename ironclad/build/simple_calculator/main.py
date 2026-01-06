import add_numbers
from add_numbers import add_numbers
import subtract_numbers
from subtract_numbers import subtract_numbers


def main():
    """Perform basic arithmetic operations on two numbers."""
    try:
        a = float(input("Enter first number: "))
        b = float(input("Enter second number: "))
    except ValueError:
        print("Invalid input. Please enter numeric values.")
        return

    try:
        sum_result = add_numbers(a, b)
        diff_result = subtract_numbers(a, b)
    except Exception as e:
        print(f"Error during arithmetic operations: {e}")
        return

    print(f"Sum: {sum_result}")
    print(f"Difference: {diff_result}")


if __name__ == "__main__":
    main()