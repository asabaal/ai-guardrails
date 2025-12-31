def add_numbers(a: float, b: float) -> float:
    """
    Return the sum of two numeric values.
    Raises ValueError if either argument is not a number (int or float).
    For floats, the result follows IEEE 754 semantics.
    """
    if not isinstance(a, (int, float)):
        raise ValueError(f"Argument 'a' must be a number, got {type(a).__name__}")
    if not isinstance(b, (int, float)):
        raise ValueError(f"Argument 'b' must be a number, got {type(b).__name__}")
    return a + b
