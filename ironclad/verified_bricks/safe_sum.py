def safe_sum(nums, default=0):
    if not isinstance(nums, (list, tuple)):
        raise TypeError("nums must be a list or tuple")
    if not nums:
        return default
    total = 0
    for num in nums:
        if not isinstance(num, (int, float)):
            raise TypeError("All elements must be numeric")
        total += num
    return total
