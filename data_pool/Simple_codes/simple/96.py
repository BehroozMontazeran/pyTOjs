def sumOfDigitsSingle(x):
    ans = 0
    while x:
        ans += x % 10
        x //= 10
    return ans


def closest(x):
    ans = 0
    while (ans * 10 + 9 <= x):
        ans = ans * 10 + 9
    return ans


def sumOfDigitsTwoParts(N):
    A = closest(N)
    return sumOfDigitsSingle(A) + sumOfDigitsSingle(N - A)


if __name__ == "__main__":
    N = 35
    print(sumOfDigitsTwoParts(N))
