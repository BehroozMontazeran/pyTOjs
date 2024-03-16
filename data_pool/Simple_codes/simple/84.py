def findMaxSum(arr, n):
    preSum = [0 for i in range(n)]
    suffSum = [0 for i in range(n)]
    ans = -  10000000
    preSum[0] = arr[0]
    for i in range(1,  n):
        preSum[i] = preSum[i - 1] + arr[i]
    suffSum[n - 1] = arr[n - 1]
    if (preSum[n - 1] == suffSum[n - 1]):
        ans = max(ans,   preSum[n - 1])
    for i in range(n - 2,  -  1,  -  1):
        suffSum[i] = suffSum[i + 1] + arr[i]
        if (suffSum[i] == preSum[i]):
            ans = max(ans,    preSum[i])
    return ans


if __name__ == "__main__":
    arr = [- 2,  5,  3,  1,  2,  6,  -  4,  2]
    n = len(arr)
    print(findMaxSum(arr,  n))
