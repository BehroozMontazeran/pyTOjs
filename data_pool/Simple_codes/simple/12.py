def countIndices(arr, n):
    cnt = 0
    max = 0
    for i in range(n):
        if (max < arr[i]):
            max = arr[i]
            cnt += 1
    return cnt


if __name__ == '__main__':
    arr = [1,  2,  3,  4]
    n = len(arr)
    print(countIndices(arr, n))
