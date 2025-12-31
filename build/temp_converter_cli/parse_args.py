import argparse


def _float_type(value: str) -> float:
    try:
        return float(value)
    except ValueError as e:
        raise argparse.ArgumentTypeError(
            f"Temperature must be a float: '{value}'"
        ) from e


def _scale_type(value: str) -> str:
    lower = value.lower()
    if lower not in ("c", "f"):
        raise argparse.ArgumentTypeError(
            f"Scale must be 'c' or 'f': '{value}'"
        )
    return lower


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Parse temperature conversion arguments."
    )
    parser.add_argument(
        "temperature",
        type=_float_type,
        help="Temperature value"
    )
    parser.add_argument(
        "scale",
        nargs="?",
        type=_scale_type,
        help="Target scale (c or f)"
    )
    parser.add_argument(
        "--to",
        dest="scale",
        type=_scale_type,
        help="Target scale (c or f)"
    )
    args = parser.parse_args()
    if args.scale is None:
        parser.error("Target scale is required")
    return args
