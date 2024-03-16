def Cells(n, x):
    if (n <= 0 or x <= 0 or x > n * n):
        return 0
    i = 1
    count = 0
    while (i * i < x):
        if (x % i == 0 and x <= n * i):
            count += 2
        i += 1
    if (i * i == x):
        return count + 1
    else:
        return count


n = 6
x = 12
print(Cells(n, x))
