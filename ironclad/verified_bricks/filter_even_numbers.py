def filter_even_numbers(numbers):
    """Return a list of even integers from the input iterable."""
    return [n for n in numbers if isinstance(n, int) and n % 2 == 0]
