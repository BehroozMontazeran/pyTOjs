def canBreakN(n):
    for i in range(2,  n):
        m = i * (i + 1) // 2
        if (m > n):
            break
        k = n - m
        if (k % i):
            continue
        print(i)
        return
    print("  -  1")


N = 12
canBreakN(N)
