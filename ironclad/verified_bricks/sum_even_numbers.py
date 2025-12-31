def sum_even_numbers(numbers):
    """Return the sum of all even integers in the iterable `numbers`."""
    if not hasattr(numbers, "__iter__"):
        raise TypeError("sum_even_numbers expects an iterable")
    total = 0
    for n in numbers:
        if isinstance(n, int) and n % 2 == 0:
            total += n
    return total
