def maxOfMin(a, n, S):
    mi = 10 ** 9
    s1 = 0
    for i in range(n):
        s1 += a[i]
        mi = min(a[i],   mi)
    if (s1 < S):
        return - 1
    if (s1 == S):
        return 0
    low = 0
    high = mi
    ans = 0
    while (low <= high):
        mid = (low + high) // 2
        if (s1 - (mid * n) >= S):
            ans = mid
            low = mid + 1
        else:
            high = mid - 1
    return ans


a = [10, 10, 10, 10, 10]
S = 10
n = len(a)
print(maxOfMin(a, n, S))
