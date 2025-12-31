import math

def validate_temperature(value: str) -> float:
    try:
        temp = float(value)
    except Exception:
        raise ValueError(f"Cannot convert '{value}' to float") from None

    if not math.isfinite(temp):
        raise ValueError(f"Temperature '{value}' is not finite")

    if not -1e6 <= temp <= 1e6:
        raise ValueError(f"Temperature {temp} out of range [-1e6, 1e6]")

    return temp
