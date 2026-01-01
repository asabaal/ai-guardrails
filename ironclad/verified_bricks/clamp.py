def clamp(value, min_value, max_value):
    """
    Return value bounded by min_value and max_value.
    If min_value is greater than max_value, the arguments are swapped.
    """
    if min_value > max_value:
        min_value, max_value = max_value, min_value
    return max(min_value, min(value, max_value))
