def maxSum1(arr, n):
    dp = [0] * n
    maxi = 0
    for i in range(n - 1):
        dp[i] = arr[i]
        if (maxi < arr[i]):
            maxi = arr[i]
    for i in range(2,  n - 1):
        for j in range(i - 1):
            if (dp[i] < dp[j] + arr[i]):
                dp[i] = dp[j] + arr[i]
                if (maxi < dp[i]):
                    maxi = dp[i]
    return maxi


def maxSum2(arr, n):
    dp = [0] * n
    maxi = 0
    for i in range(1,  n):
        dp[i] = arr[i]
        if (maxi < arr[i]):
            maxi = arr[i]
    for i in range(3,  n):
        for j in range(1,   i - 1):
            if (dp[i] < arr[i] + dp[j]):
                dp[i] = arr[i] + dp[j]
                if (maxi < dp[i]):
                    maxi = dp[i]
    return maxi


def findMaxSum(arr, n):
    return max(maxSum1(arr,  n),  maxSum2(arr,  n))


if __name__ == "__main__":
    arr = [1,  2,  3,  1]
    n = len(arr)
    print(findMaxSum(arr,  n))
