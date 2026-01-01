def calculate_average(numbers: list[float]) -> float:
    """Return the average of a non-empty list of numbers.

    Parameters:
        numbers: A list of numeric values.

    Returns:
        The arithmetic mean of the elements.

    Raises:
        ValueError: If the input list is empty.
    """
    if not numbers:
        raise ValueError("Input list must not be empty")
    return sum(numbers) / len(numbers)
