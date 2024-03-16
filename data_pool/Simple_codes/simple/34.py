def compute_z(s, z):
    l = 0
    r = 0
    n = len(s)
    for i in range(1,  n,  1):
        if (i > r):
            l = i
            r = i
            while (r < n and s[r - l] == s[r]):
                r += 1
            z[i] = r - l
            r -= 1
        else:
            k = i - l
            if (z[k] < r - i + 1):
                z[i] = z[k]
            else:
                l = i
                while (r < n and s[r - l] == s[r]):
                    r += 1
                z[i] = r - l
                r -= 1


def countPermutation(a, b):
    b = b + b
    b = b[0:  len(b) - 1]
    ans = 0
    s = a + "  $  " + b
    n = len(s)
    z = [0 for i in range(n)]
    compute_z(s,  z)
    for i in range(1,  n,  1):
        if (z[i] == len(a)):
            ans += 1
    return ans


if __name__ == '__main__':
    a = "101"
    b = "101"
    print(countPermutation(a,  b))
