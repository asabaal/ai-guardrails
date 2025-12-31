def fahrenheit_to_celsius(fahrenheit: float) -> float:
    '''
    Convert Fahrenheit to Celsius using the formula C = (F - 32) * 5/9.
    Raises TypeError if the input is None or not a numeric value.
    '''
    if fahrenheit is None:
        raise TypeError('Input cannot be None')
    try:
        f = float(fahrenheit)
    except (TypeError, ValueError) as e:
        raise TypeError('Input must be a number') from e
    return (f - 32) * 5.0 / 9.0
