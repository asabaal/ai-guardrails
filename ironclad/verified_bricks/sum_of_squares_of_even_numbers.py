def sum_of_squares_of_even_numbers(numbers):
    if not isinstance(numbers, list):
        raise TypeError("Input must be a list")
    return sum(x * x for x in numbers if isinstance(x, int) and x % 2 == 0)
