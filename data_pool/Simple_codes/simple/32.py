def permutationCoeff(n, k):
    fact = [0 for i in range(n + 1)]
    fact[0] = 1
    for i in range(1,  n + 1):
        fact[i] = i * fact[i - 1]
    return int(fact[n] / fact[n - k])


n = 10
k = 2
print(" Value ▁ of ▁ P ( ", n, " , ▁ ", k, " ) ▁ is ▁ ",
      permutationCoeff(n, k), sep=" ")
