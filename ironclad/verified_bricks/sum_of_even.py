def sum_of_even(numbers):
    """Return the sum of all even integers in the sequence.

    Parameters
    ----------
    numbers : Iterable[int]
        A list or tuple of integers.

    Returns
    -------
    int
        Sum of the even numbers; zero if none.
    """
    if not isinstance(numbers, (list, tuple)):
        raise TypeError("Input must be a list or tuple of integers")
    total = 0
    for n in numbers:
        if not isinstance(n, int):
            raise TypeError("All elements must be integers")
        if n % 2 == 0:
            total += n
    return total
