def format_output(value: float, unit: str) -> str:
    import math
    if unit not in ("C", "F"):
        raise ValueError(f"Invalid unit: {unit}. Expected 'C' or 'F'.")
    if math.isnan(value) or math.isinf(value):
        return f"{value} °{unit}"
    rounded = round(value, 1)
    return f"{rounded:.1f} °{unit}"
