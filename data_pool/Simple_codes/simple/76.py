import sys

def print2Smallest(arr):
    arr_size = len(arr)
    if arr_size < 2:
        print("Invalid Input")
        return

    first = second = sys.maxsize

    for i in range(0, arr_size):
        if arr[i] < first:
            second = first
            first = arr[i]
        elif arr[i] < second and arr[i] != first:
            second = arr[i]

    if second == sys.maxsize:
        print("No second smallest element")
    else:
        print('The smallest element is', first, 'and the second smallest element is', second)

arr = [12, 13, 1, 10, 34, 1]
print2Smallest(arr)
