def is_prime(n):
    """Return True if n is a prime number, False otherwise.

    Parameters:
        n (int): The number to test.

    Returns:
        bool: True if n is prime, False otherwise.
    """
    if not isinstance(n, int):
        raise TypeError("Input must be an integer")
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    w = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += w
        w = 6 - w
    return True