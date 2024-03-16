def printTetra(n):
    dp = [0] * (n + 5)
    dp[0] = 0
    dp[1] = 1
    dp[2] = 1
    dp[3] = 2
    for i in range(4,  n + 1):
        dp[i] = (dp[i - 1] + dp[i - 2] + dp[i - 3] + dp[i - 4])
    print(dp[n])


n = 10
printTetra(n)
