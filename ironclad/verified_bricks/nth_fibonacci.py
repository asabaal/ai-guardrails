def nth_fibonacci(n):
    """Return the *n*th Fibonacci number.

    The sequence is defined as:

    * F(0) = 0
    * F(1) = 1
    * F(n) = F(n-1) + F(n-2) for n > 1

    Parameters
    ----------
    n : int
        Non‑negative integer index of the Fibonacci sequence.

    Returns
    -------
    int
        The *n*th Fibonacci number.

    Raises
    ------
    TypeError
        If *n* is not an integer.
    ValueError
        If *n* is negative.
    """
    if not isinstance(n, int):
        raise TypeError("n must be an integer")
    if n < 0:
        raise ValueError("n must be non‑negative")
    # Base cases
    if n == 0:
        return 0
    if n == 1:
        return 1
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
