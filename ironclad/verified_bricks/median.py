def median(nums: list[float]) -> float:
    """Return median of a non-empty list of numbers.
    Raises ValueError if list is empty."""
    if not nums:
        raise ValueError("Cannot compute median of an empty list")
    sorted_nums = sorted(nums)
    n = len(sorted_nums)
    mid = n // 2
    if n % 2 == 1:
        return float(sorted_nums[mid])
    else:
        return (sorted_nums[mid - 1] + sorted_nums[mid]) / 2.0
