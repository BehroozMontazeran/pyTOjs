import numpy as np
n = 3
dp = np . zeros((n, n))
v = np . zeros((n, n))


def minSteps(i, j, arr):
    if (i == n - 1 and j == n - 1):
        return 0
    if (i > n - 1 or j > n - 1):
        return 9999999
    if (v[i][j]):
        return dp[i][j]
    v[i][j] = 1
    dp[i][j] = 9999999
    for k in range(max(0,  arr[i][j] + j - n + 1),
                   min(n - i - 1,  arr[i][j]) + 1):
        dp[i][j] = min(dp[i][j],   minSteps(i + k,   j + arr[i][j] - k,   arr))
    dp[i][j] += 1
    return dp[i][j]


if __name__ == "__main__":
    arr = [[4,  1,  2],  [1,  1,  1],  [2,  1,  1]]
    ans = minSteps(0,  0,  arr)
    if (ans >= 9999999):
        print(- 1)
    else:
        print(ans)
