import math
MAX = 10000
primes = []


def sieveSundaram():
    marked = [False] * ((MAX // 2) + 1)
    for i in range(1,  ((int(math  .  sqrt(MAX)) - 1) // 2) + 1):
        j = (i * (i + 1)) << 1
        while j <= (MAX // 2):
            marked[j] = True
            j = j + 2 * i + 1
    primes  .  append(2)
    for i in range(1,  (MAX // 2) + 1):
        if not marked[i]:
            primes    .    append(2 * i + 1)


def isWasteful(n):
    if (n == 1):
        return False
    original_no = n
    sumDigits = 0
    while (original_no > 0):
        sumDigits += 1
        original_no = original_no // 10
    pDigit,  count_exp,  p = 0,  0,  0
    i = 0
    while (primes[i] <= (n // 2)):
        while (n % primes[i] == 0):
            p = primes[i]
            n = n // p
            count_exp += 1
        while (p > 0):
            pDigit += 1
            p = p // 10
        while (count_exp > 1):
            pDigit += 1
            count_exp = count_exp // 10
        i += 1
    if (n != 1):
        while (n > 0):
            pDigit += 1
            n = n // 10
    return bool(pDigit > sumDigits)


def Solve(N):
    for i in range(1,  N):
        if (isWasteful(i)):
            print(i,    end="    ▁    ")


sieveSundaram()
N = 10
Solve(N)
