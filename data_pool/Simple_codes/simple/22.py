import numpy as np
n = 6
m = 6


def maxSum(arr):
    dp = np  .  zeros((n + 1,  3))
    for i in range(n):
        m1 = 0
        m2 = 0
        m3 = 0
        for j in range(m):
            if ((j // (m // 3)) == 0):
                m1 = max(m1,     arr[i][j])
            elif ((j // (m // 3)) == 1):
                m2 = max(m2,     arr[i][j])
            elif ((j // (m // 3)) == 2):
                m3 = max(m3,     arr[i][j])
        dp[i + 1][0] = max(dp[i][1],   dp[i][2]) + m1
        dp[i + 1][1] = max(dp[i][0],   dp[i][2]) + m2
        dp[i + 1][2] = max(dp[i][1],   dp[i][0]) + m3
    print(max(max(dp[n][0],  dp[n][1]),  dp[n][2]))


if __name__ == "__main__":
    arr = [
        [
            1,  3,  5,  2,  4,  6],  [
            6,  4,  5,  1,  3,  2],  [
                1,  3,  5,  2,  4,  6],  [
                    6,  4,  5,  1,  3,  2],  [
                        6,  4,  5,  1,  3,  2],  [
                            1,  3,  5,  2,  4,  6]]
    maxSum(arr)
