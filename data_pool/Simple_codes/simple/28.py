MAX = 1001
dp = [[-1 for _ in range(MAX)] for _ in range(MAX)]

def MaxProfit(treasure, color, n, k, col, A, B):
    if (k == n):
        dp[k][col] = 0
        return dp[k][col]
    if (dp[k][col] != -1):
        return dp[k][col]
    summ = 0
    if (col == color[k]):
        summ += max(A * treasure[k] + MaxProfit(treasure,
                                                color,
                                                n,
                                                k + 1,
                                                color[k],
                                                A,
                                                B),
                    MaxProfit(treasure,
                              color,
                              n,
                              k + 1,
                              col,
                              A,
                              B))
    else:
        summ += max(B * treasure[k] + MaxProfit(treasure,
                                                color,
                                                n,
                                                k + 1,
                                                color[k],
                                                A,
                                                B),
                    MaxProfit(treasure,
                              color,
                              n,
                              k + 1,
                              col,
                              A,
                              B))
    dp[k][col] = summ
    return dp[k][col]

A = -5
B = 7
treasure = [4, 8, 2, 9]
color = [2, 2, 6, 2]
n = len(color)
print(MaxProfit(treasure, color, n, 0, 0, A, B))
