def max_product_pair(nums):
    """
    Return the maximum product of any two integers in the list.
    Non-integer elements are ignored.
    Raises ValueError if less than two integers are present.
    """
    ints = [x for x in nums if isinstance(x, int)]
    if len(ints) < 2:
        raise ValueError("Need at least two integers")
    ints.sort()
    prod1 = ints[0] * ints[1]
    prod2 = ints[-1] * ints[-2]
    return max(prod1, prod2)
