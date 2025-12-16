def add_two_numbers(a, b):
    '''Return the sum of two numbers.
    
    Parameters:
    a: int or float
    b: int or float
    
    Raises:
    TypeError: if either argument is not an int or float.
    '''
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Both arguments must be int or float")
    return a + b