def fibonacci(n):
    """Return the nth Fibonacci number.

    Parameters
    ----------
    n : int
        The position in the Fibonacci sequence (0-indexed).

    Returns
    -------
    int
        The nth Fibonacci number.

    Raises
    ------
    TypeError
        If ``n`` is not an integer.
    ValueError
        If ``n`` is negative.
    """
    if not isinstance(n, int):
        raise TypeError("n must be an integer")
    if n < 0:
        raise ValueError("n must be non-negative")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a