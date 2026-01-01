def sum_list(numbers):
    """Return the sum of a list of numbers.

    Parameters
    ----------
    numbers : list
        A list containing integers or floats.

    Returns
    -------
    int or float
        The sum of the list elements.

    Raises
    ------
    TypeError
        If *numbers* is not a list, or any element is not an int or float.
    """
    if not isinstance(numbers, list):
        raise TypeError('Input must be a list')
    total = 0
    for n in numbers:
        if not isinstance(n, (int, float)):
            raise TypeError('All elements must be int or float')
        total += n
    return total
