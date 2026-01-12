def multiply_list(nums: list[int]) -> int:
    """Return the product of all integers in the list. Return 1 for empty list."""
    prod = 1
    for n in nums:
        prod *= n
    return prod
