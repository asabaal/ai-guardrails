def sum_positive_numbers(numbers):
    if not isinstance(numbers, list):
        raise TypeError("Input must be a list")
    total = 0
    for num in numbers:
        if not isinstance(num, (int, float)):
            raise TypeError("All items must be int or float")
        if num > 0:
            total += num
    return total
