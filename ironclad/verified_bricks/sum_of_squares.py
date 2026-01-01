def sum_of_squares(numbers):
    """Return the sum of squares of the elements in numbers.

    Parameters:
    numbers: iterable of numbers (int, float)

    Returns:
    int or float sum of squares.
    Raises:
    TypeError if numbers is not iterable or contains non-numeric elements.
    """
    total = 0
    for n in numbers:
        if not isinstance(n, (int, float)):
            raise TypeError("All elements must be int or float")
        total += n * n
    return total
