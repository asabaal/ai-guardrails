def add_numbers(a: float, b: float) -> float:
    """
    Add two numbers and return the result as a float.

    Parameters
    ----------
    a : float
        First operand.
    b : float
        Second operand.

    Returns
    -------
    float
        The sum ``float(a) + float(b)``.  The return type is always a float
        regardless of the input types.  Special float values such as NaN and
        infinities are handled according to the standard floating‑point rules.
    """
    return float(a) + float(b)