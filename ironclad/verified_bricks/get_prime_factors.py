def get_prime_factors(n):
    """
    Return the list of prime factors of a positive integer n.
    Raises ValueError for non-positive inputs or non-integer types.
    """
    if not isinstance(n, int):
        raise ValueError("Input must be an integer")
    if n <= 0:
        raise ValueError("Input must be a positive integer")
    factors = []
    while n % 2 == 0:
        factors.append(2)
        n //= 2
    p = 3
    while p * p <= n:
        while n % p == 0:
            factors.append(p)
            n //= p
        p += 2
    if n > 1:
        factors.append(n)
    return factors