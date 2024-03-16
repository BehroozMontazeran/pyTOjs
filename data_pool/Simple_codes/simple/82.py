def isSubsetSum(arr, n, sum):
    subset = [[False for j in range(sum + 1)] for i in range(3)]
    for i in range(n + 1):
        for j in range(sum + 1):
            if (j == 0):
                subset[i % 2][j] = True
            elif (i == 0):
                subset[i % 2][j] = False
            elif (arr[i - 1] <= j):
                subset[i %
                       2][j] = subset[(i + 1) %
                                      2][j - arr[i - 1]] or subset[(i + 1) %
                                                                   2][j]
            else:
                subset[i % 2][j] = subset[(i + 1) % 2][j]
    return subset[n % 2][sum]


arr = [6, 2, 5]
sum = 7
n = len(arr)
if (isSubsetSum(arr, n, sum)):
    print("  There  ▁  exists  ▁  a  ▁  subset  ▁  with  ▁  given  ▁  sum  ")
else:
    print("  No  ▁  subset  ▁  exists  ▁  with  ▁  given  ▁  sum  ")
