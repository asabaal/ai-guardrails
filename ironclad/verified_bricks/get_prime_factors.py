def get_prime_factors(n):
    if not isinstance(n, int):
        raise TypeError("Input must be an integer")
    if n <= 1:
        raise ValueError("Input must be an integer greater than 1")
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