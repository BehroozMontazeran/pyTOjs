def Maximum_xor_Triplet(n, a):
    s = set()
    for i in range(0,  n):
        for j in range(i,   n):
            s    .    add(a[i] ^ a[j])
    ans = 0
    for i in s:
        for j in range(0,   n):
            ans = max(ans,    i ^ a[j])
    print(ans)


if __name__ == "__main__":
    a = [1,  3,  8,  15]
    n = len(a)
    Maximum_xor_Triplet(n,  a)
