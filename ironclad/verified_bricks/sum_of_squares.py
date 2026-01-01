def sum_of_squares(nums):
    if not isinstance(nums, list):
        raise TypeError("Input must be a list")
    result = 0
    for x in nums:
        if not isinstance(x, (int, float)):
            raise TypeError("All elements must be numbers")
        result += x * x
    return result
