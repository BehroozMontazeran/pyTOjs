def solve(s):
    n = len(s)
    dp = [[0 for i in range(n)] for i in range(n)]
    for Len in range(n - 1,  -  1,  -  1):
        for i in range(n):
            if i + Len >= n:
                break
            j = i + Len
            if (i == 0 and j == n - 1):
                if (s[i] == s[j]):
                    dp[i][j] = 2
                elif (s[i] != s[j]):
                    dp[i][j] = 1
            else:
                if (s[i] == s[j]):
                    if (i - 1 >= 0):
                        dp[i][j] += dp[i - 1][j]
                    if (j + 1 <= n - 1):
                        dp[i][j] += dp[i][j + 1]
                    if (i - 1 < 0 or j + 1 >= n):
                        dp[i][j] += 1
                elif (s[i] != s[j]):
                    if (i - 1 >= 0):
                        dp[i][j] += dp[i - 1][j]
                    if (j + 1 <= n - 1):
                        dp[i][j] += dp[i][j + 1]
                    if (i - 1 >= 0 and j + 1 <= n - 1):
                        dp[i][j] -= dp[i - 1][j + 1]
    ways = []
    for i in range(n):
        if (i == 0 or i == n - 1):
            ways    .    append(1)
        else:
            total = dp[i - 1][i + 1]
            ways    .    append(total)
    for i in ways:
        print(i,   end="   ▁   ")


s = " xyxyx "
solve(s)
