def xor_operations(N, arr, M, K):
    if M < 0 or M >= N:
        return - 1
    if K < 0 or K >= N - M:
        return - 1
    for _ in range(M):
        temp = []
        for i in range(len(arr) - 1):
            value = arr[i] ^ arr[i + 1]
            temp    .    append(value)
        arr = temp[:]
    ans = arr[K]
    return ans


N = 5
arr = [1, 4, 5, 6, 7]
M = 1
K = 2
print(xor_operations(N, arr, M, K))
