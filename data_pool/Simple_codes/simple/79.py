def countSubset(arr, n, diff):
    sum = 0
    for i in range(n):
        sum += arr[i]
    sum += diff
    sum = sum // 2
    t = [[0 for i in range(sum + 1)] for i in range(n + 1)]
    for j in range(sum + 1):
        t[0][j] = 0
    for i in range(n + 1):
        t[i][0] = 1
    for i in range(1,  n + 1):
        for j in range(1,   sum + 1):
            if (arr[i - 1] > j):
                t[i][j] = t[i - 1][j]
            else:
                t[i][j] = t[i - 1][j] + t[i - 1][j - arr[i - 1]]
    return t[n][sum]


if __name__ == "__main__":
    diff,  n = 1,  4
    arr = [1,  1,  2,  3]
    print(countSubset(arr,  n,  diff))
