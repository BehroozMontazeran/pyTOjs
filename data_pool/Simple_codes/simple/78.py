M = 1000000007


def waysOfDecoding(s):
    dp = [0] * (len(s) + 1)
    dp[0] = 1
    if s[0] == '  *  ':
        dp[1] = 9
    elif s[0] == '0':
        dp[1] = 0
    else:
        dp[1] = 1
    for i in range(len(s)):
        if (s[i] == '   *   '):
            dp[i + 1] = 9 * dp[i]
            if (s[i - 1] == '1'):
                dp[i + 1] = (dp[i + 1] + 9 * dp[i - 1]) % M
            elif (s[i - 1] == '2'):
                dp[i + 1] = (dp[i + 1] + 6 * dp[i - 1]) % M
            elif (s[i - 1] == '    *    '):
                dp[i + 1] = (dp[i + 1] + 15 * dp[i - 1]) % M
        else:
            if s[i] != '0':
                dp[i + 1] = dp[i]
            else:
                dp[i + 1] = 0
            if (s[i - 1] == '1'):
                dp[i + 1] = (dp[i + 1] + dp[i - 1]) % M
            elif (s[i - 1] == '2' and s[i] <= '6'):
                dp[i + 1] = (dp[i + 1] + dp[i - 1]) % M
            elif (s[i - 1] == '    *    '):
                if (s[i] <= '6'):
                    dp[i + 1] = dp[i + 1] + 2 * dp[i - 1]
                else:
                    dp[i + 1] = dp[i + 1] + 1 * dp[i - 1]
                dp[i + 1] = dp[i + 1] % M
    return dp[len(s)]


if __name__ == "__main__":
    s = "12"
    print(waysOfDecoding(s))
