import math

def convert_to_float(value: str) -> float:
    """Attempt to convert a string to a float.

    Parameters
    ----------
    value : str
        The string to be converted to a float.

    Returns
    -------
    float
        The numeric float representation of the input string.

    Raises
    ------
    ValueError
        If the input is not a string or cannot be converted to a float.
    """
    if not isinstance(value, str):
        raise ValueError(f"Expected a string, got {type(value).__name__}.")
    try:
        result = float(value)
    except ValueError as exc:
        raise ValueError(f"Unable to convert '{value}' to float.") from exc
    if math.isnan(result):
        raise ValueError(f"Unable to convert '{value}' to float.")
    return result
