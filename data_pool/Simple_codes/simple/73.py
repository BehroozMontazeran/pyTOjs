def search(arr, l, h, key):
    if l > h:
        return -1
    mid = (l + h) // 2
    if arr[mid] == key:
        return mid
    if arr[l] <= arr[mid]:
        if key >= arr[l] and key <= arr[mid]:
            return search(arr, l, mid - 1, key)
        return search(arr, mid + 1, h, key)
    if key >= arr[mid] and key <= arr[h]:
        return search(arr, mid + 1, h, key)
    return search(arr, l, mid - 1, key)

arr = [4, 5, 6, 7, 8, 9, 1, 2, 3]
key = 6
i = search(arr, 0, len(arr) - 1, key)
if i != -1:
    print("Index: %d" % i)
else:
    print("Key not found")
