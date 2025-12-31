def validate_temperature(temp_str: str) -> float:
    try:
        return float(temp_str)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid temperature string: {temp_str!r}") from None
