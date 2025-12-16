def to_number(value: str) -> float:
    """Convert a string to a floating‑point number.

    Supports integers, decimals, and scientific notation.
    Raises a ValueError with an informative message if the string cannot
    be parsed into a float.

    Parameters
    ----------
    value : str
        The string representation of a number.

    Returns
    -------
    float
        The parsed floating‑point number.
    """
    if not isinstance(value, str):
        raise ValueError(f'Input must be a string, got {type(value).__name__}')
    stripped = value.strip()
    if stripped == '':
        raise ValueError('Cannot convert empty string to float.')
    try:
        return float(stripped)
    except ValueError as e:
        raise ValueError(f"Cannot convert '{value}' to float.") from e