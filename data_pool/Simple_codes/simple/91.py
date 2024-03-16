def Maximum_Length(a):
    counts = [0] * 11
    for index,  v in enumerate(a):
        counts[v] += 1
        k = sorted([i for i in counts if i])
        if len(k) == 1 or (k[0] == k[- 2] and k[- 1] -
                           k[- 2] == 1) or (k[0] == 1 and k[1] == k[- 1]):
            ans = index
    return ans + 1


if __name__ == "__main__":
    a = [1,  1,  1,  2,  2,  2]
    n = len(a)
    print(Maximum_Length(a))
