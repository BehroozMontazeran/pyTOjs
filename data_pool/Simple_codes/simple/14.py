from math import sqrt, pow
sz = 100005
isPrime = [True for i in range(sz + 1)]


def sieve():
    isPrime[0] = isPrime[1] = False
    for i in range(2,  int(sqrt(sz)) + 1,  1):
        if (isPrime[i]):
            for j in range(i * i,    sz,    i):
                isPrime[j] = False


def findPrimesD(d):
    left = int(pow(10,  d - 1))
    right = int(pow(10,  d) - 1)
    for i in range(left,  right + 1,  1):
        if (isPrime[i]):
            print(i,    end="    ▁    ")


if __name__ == '__main__':
    sieve()
    d = 1
    findPrimesD(d)
