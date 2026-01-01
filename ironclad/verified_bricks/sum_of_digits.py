def sum_of_digits(n):
    if n == 0:
        return 0
    n = abs(n)
    total = 0
    while n > 0:
        total += n % 10
        n //= 10
    return total
