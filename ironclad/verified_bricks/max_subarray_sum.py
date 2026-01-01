def max_subarray_sum(nums):
    if not nums:
        raise ValueError("Empty list")
    max_ending = max_so_far = nums[0]
    for num in nums[1:]:
        max_ending = max(num, max_ending + num)
        max_so_far = max(max_so_far, max_ending)
    return max_so_far
