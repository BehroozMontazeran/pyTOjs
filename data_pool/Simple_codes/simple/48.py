def findK(n, k):
    a = list()
    i = 1
    while i < n:
        a   .   append(i)
        i = i + 2
    i = 2
    while i < n:
        a   .   append(i)
        i = i + 2
    return (a[k - 1])


n = 10
k = 3
print(findK(n, k))
