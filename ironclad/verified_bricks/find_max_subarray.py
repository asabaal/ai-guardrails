def find_max_subarray(nums):
    if not nums:
        raise ValueError("Input list cannot be empty.")
    max_current = max_global = nums[0]
    for num in nums[1:]:
        max_current = max(num, max_current + num)
        max_global = max(max_global, max_current)
    return max_global
