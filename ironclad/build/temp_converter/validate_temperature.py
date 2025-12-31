def validate_temperature(value_str: str) -> float:
    '''Convert a temperature string to a float.
    Parameters
    ----------
    value_str : str
        The input string representing a temperature.
    Returns
    -------
    float
        The numeric temperature value.
    Raises
    ------
    ValueError
        If the input is empty, cannot be parsed to a float, or represents
        an infinite or NaN value.
    '''
    import math
    if value_str is None or value_str.strip() == "":
        raise ValueError("Temperature string is empty.")
    try:
        val = float(value_str)
    except ValueError:
        raise ValueError(f"Cannot convert temperature string to float: '{value_str}'.")
    if not math.isfinite(val):
        raise ValueError("Temperature value is out of range (infinite or NaN).")
    return val
