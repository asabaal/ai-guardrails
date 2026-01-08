def count_doublings(a, b):
    """
    Return the minimum number of times you must double ``a`` to reach
    or exceed ``b``.

    Parameters
    ----------
    a : int
        Starting value (must be positive).
    b : int
        Target value (must be positive).

    Returns
    -------
    int
        Number of doublings required.

    Raises
    ------
    ValueError
        If either ``a`` or ``b`` is not a positive integer.
    """
    if not isinstance(a, int) or not isinstance(b, int):
        raise ValueError("Both a and b must be integers")
    if a <= 0 or b <= 0:
        raise ValueError("Both a and b must be positive integers")
    if a >= b:
        return 0
    count = 0
    while a < b:
        a *= 2
        count += 1
    return count
