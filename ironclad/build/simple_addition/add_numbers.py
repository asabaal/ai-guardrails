def add_numbers(a: float, b: float) -> float:
    """Return the sum of two numbers.

    Parameters
    ----------
    a : int | float
        First numeric argument.
    b : int | float
        Second numeric argument.

    Returns
    -------
    float
        The sum of ``a`` and ``b`` coerced to a float.

    Raises
    ------
    TypeError
        If either ``a`` or ``b`` is not an ``int`` or ``float``.
    """
    if not isinstance(a, (int, float)):
        raise TypeError(f"Argument 'a' must be int or float, got {type(a).__name__}")
    if not isinstance(b, (int, float)):
        raise TypeError(f"Argument 'b' must be int or float, got {type(b).__name__}")
    return float(a) + float(b)
