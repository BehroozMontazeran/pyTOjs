def countSubarrays(A):
    res = 0
    curr,  cnt = A[0],  [1]
    for c in A[1:]:
        if c == curr:
            cnt[- 1] += 1
        else:
            curr = c
        cnt   .   append(1)
    for i in range(1,  len(cnt)):
        res += min(cnt[i - 1],   cnt[i])
    print(res - 1)


##Driver code * /
A = [1, 1, 0, 0, 1, 0]
countSubarrays(A)
