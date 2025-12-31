import sys

from parse_args import parse_args
from validate_temperature import validate_temperature
from celsius_to_fahrenheit import celsius_to_fahrenheit
from format_output import format_output


def fahrenheit_to_celsius(f_temp: float) -> float:
    """Convert Fahrenheit to Celsius."""
    return (f_temp - 32) * 5 / 9


def main():
    try:
        args = parse_args()
        temperature = validate_temperature(args.value)

        unit = args.unit.lower()
        if unit in ("c", "celsius", "°c", "c°"):
            converted = celsius_to_fahrenheit(temperature)
            target_unit = "F"
        elif unit in ("f", "fahrenheit", "°f", "f°"):
            converted = fahrenheit_to_celsius(temperature)
            target_unit = "C"
        else:
            raise ValueError(f"Unknown unit '{args.unit}'. Use 'C' or 'F'.")

        output = format_output(converted, target_unit)
        print(output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
