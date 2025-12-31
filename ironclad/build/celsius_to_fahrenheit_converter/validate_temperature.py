def validate_temperature(value: float) -> bool:
    if isinstance(value, (int, float)):
        return True
    return False
