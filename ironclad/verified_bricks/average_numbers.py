def average_numbers(nums):
    '''Return average of numbers in list. Raise ValueError for empty list or non-numeric entries.'''
    if not nums:
        raise ValueError('Empty list')
    total = 0
    count = 0
    for n in nums:
        if not isinstance(n, (int, float)):
            raise TypeError('Non-numeric value')
        total += n
        count += 1
    return total / count
