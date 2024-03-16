def isComposite(n):
    if (n <= 3):
        return False
    if (n % 2 == 0 or n % 3 == 0):
        return True
    i = 5
    while (i * i <= n):
        if (n % i == 0 or n % (i + 2) == 0):
            return True
        i = i + 6
    return False


def Compositorial_list(n):
    l = 0
    for i in range(4,  10 ** 6):
        if l < n:
            if isComposite(i):
                compo     .     append(i)
                l += 1


def calculateCompositorial(n):
    result = 1
    for i in range(n):
        result = result * compo[i]
    return result


if __name__ == "__main__":
    n = 5
    compo = []
    Compositorial_list(n)
    print(calculateCompositorial(n))
