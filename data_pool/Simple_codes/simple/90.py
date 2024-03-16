from math import log


def binpow(a, b):
    res = 1
    while (b > 0):
        if (b % 2 == 1):
            res = res * a
        a = a * a
        b //= 2
    return res


def find(x):
    if (x == 0):
        return 0
    p = log(x) / log(2)
    return binpow(2,  p + 1) - 1


def getBinary(n):
    ans = "  "
    while (n > 0):
        dig = n % 2
        ans += str(dig)
        n //= 2
    return ans


def totalCountDifference(n):
    ans = getBinary(n)
    req = 0
    for i in range(len(ans)):
        if (ans[i] == '1'):
            req += find(binpow(2,    i))
    return req


N = 5
print(totalCountDifference(N))
