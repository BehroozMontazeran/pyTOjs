def gcd(a, b):
    if a == 0:
        return b
    return gcd(b % a,  a)


def print_gcd_online(n, m, query, arr):
    max_gcd = 0
    for i in range(0,  n):
        max_gcd = gcd(max_gcd,   arr[i])
    for i in range(0,  m):
        query[i][0] -= 1
        arr[query[i][0]] //= query[i][1]
        max_gcd = gcd(arr[query[i][0]],   max_gcd)
        print(max_gcd)


if __name__ == "__main__":
    n,  m = 3,  3
    query = [[1,  3],  [3,  12],  [2,  4]]
    arr = [36,  24,  72]
    print_gcd_online(n,  m,  query,  arr)
