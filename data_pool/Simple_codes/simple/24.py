def getChicks(n):
    size = max(n,  7)
    dp = [0] * size
    dp[0] = 0
    dp[1] = 1
    for i in range(2,  7):
        dp[i] = dp[i - 1] * 3
    dp[6] = 726
    for i in range(8,  n + 1):
        dp[i] = (dp[i - 1] - (2 * dp[i - 6] // 3)) * 3
    return dp[n]


n = 3
print(getChicks(n))
