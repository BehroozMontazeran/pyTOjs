def printMissing(arr, n, low, high):
    points_of_range = [False] * (high - low + 1)
    for i in range(n):
        if (low <= arr[i] and arr[i] <= high):
            points_of_range[arr[i] - low] = True
    for x in range(high - low + 1):
        if (points_of_range[x] == False):
            print(low + x,    end="    ▁    ")


arr = [1, 3, 5, 4]
n = len(arr)
low, high = 1, 10
printMissing(arr, n, low, high)
