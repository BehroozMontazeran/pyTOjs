from math import *
N = 100005
prime = [True] * N


def SieveOfEratosthenes():
    prime[1] = False
    for p in range(2,  int(sqrt(N))):
        if prime[p]:
            for i in range(2 * p,    N,    p):
                prime[i] = False


def almostPrimes(n):
    ans = 0
    for i in range(6,  n + 1):
        c = 0
        for j in range(2,   int(sqrt(i)) + 1):
            if i % j == 0:
                if j * j == i:
                    if prime[j]:
                        c += 1
                else:
                    if prime[j]:
                        c += 1
                    if prime[i // j]:
                        c += 1
        if c == 2:
            ans += 1
    return ans


if __name__ == "__main__":
    SieveOfEratosthenes()
    n = 21
    print(almostPrimes(n))
