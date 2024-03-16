def countOddPrimeFactors(n):
    result = 1
    while (n % 2 == 0):
        n /= 2
    i = 3
    while i * i <= n:
        divCount = 0
        while (n % i == 0):
            n /= i
            divCount = divCount + 1
        result = result * divCount + 1
        i = i + 2
    if (n > 2):
        result = result * 2
    return result


def politness(n):
    return countOddPrimeFactors(n) - 1


n = 90
print ("Politness▁of ▁", n, " ▁ = ▁ ", politness(n))
n = 15
print (" Politness ▁ of ▁ ", n, " ▁ = ▁ ", politness(n))
