def gcd(a, b):
    if a == 0 and b == 0:
        raise ValueError("Both arguments cannot be zero")
    return abs(_gcd(abs(a), abs(b)))

def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a
