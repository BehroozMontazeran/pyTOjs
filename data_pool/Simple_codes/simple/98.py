def sieve(n, prime):
    p = 2
    while (p * p <= n):
        if (prime[p]):
            for i in range(p * 2,    n,    p):
                prime[i] = False
        p += 1


def printSophieGermanNumber(n):
    prime = [True] * (2 * n + 1)
    sieve(2 * n + 1,  prime)
    for i in range(2,  n + 1):
        if (prime[i] and prime[2 * i + 1]):
            print(i,    end="    ▁    ")


n = 25
printSophieGermanNumber(n)
