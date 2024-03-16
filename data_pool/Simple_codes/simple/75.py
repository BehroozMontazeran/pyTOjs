def findMin(arr, low, high):
    while (low < high):
        mid = low + (high - low) // 2
        if (arr[mid] == arr[high]):
            high -= 1
        elif (arr[mid] > arr[high]):
            low = mid + 1
        else:
            high = mid
    return arr[high]


if __name__ == "__main__":
    arr1 = [5,  6,  1,  2,  3,  4]
    n1 = len(arr1)
    print(
        "  The  ▁  minimum  ▁  element  ▁  is  ▁  ",
        findMin(
            arr1,
            0,
            n1 -
            1))
    arr2 = [1,  2,  3,  4]
    n2 = len(arr2)
    print(
        "  The  ▁  minimum  ▁  element  ▁  is  ▁  ",
        findMin(
            arr2,
            0,
            n2 -
            1))
    arr3 = [1]
    n3 = len(arr3)
    print(
        "  The  ▁  minimum  ▁  element  ▁  is  ▁  ",
        findMin(
            arr3,
            0,
            n3 -
            1))
    arr4 = [1,  2]
    n4 = len(arr4)
    print(
        "  The  ▁  minimum  ▁  element  ▁  is  ▁  ",
        findMin(
            arr4,
            0,
            n4 -
            1))
    arr5 = [2,  1]
    n5 = len(arr5)
    print(
        "  The  ▁  minimum  ▁  element  ▁  is  ▁  ",
        findMin(
            arr5,
            0,
            n5 -
            1))
    arr6 = [5,  6,  7,  1,  2,  3,  4]
    n6 = len(arr6)
    print(
        "  The  ▁  minimum  ▁  element  ▁  is  ▁  ",
        findMin(
            arr6,
            0,
            n6 -
            1))
    arr7 = [1,  2,  3,  4,  5,  6,  7]
    n7 = len(arr7)
    print(
        "  The  ▁  minimum  ▁  element  ▁  is  ▁  ",
        findMin(
            arr7,
            0,
            n7 -
            1))
    arr8 = [2,  3,  4,  5,  6,  7,  8,  1]
    n8 = len(arr8)
    print(
        "  The  ▁  minimum  ▁  element  ▁  is  ▁  ",
        findMin(
            arr8,
            0,
            n8 -
            1))
    arr9 = [3,  4,  5,  1,  2]
    n9 = len(arr9)
    print(
        "  The  ▁  minimum  ▁  element  ▁  is  ▁  ",
        findMin(
            arr9,
            0,
            n9 -
            1))
