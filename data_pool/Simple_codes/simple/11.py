from math import pow


def findSum(N, k):
    sum = 0
    for i in range(1, N + 1,  1):
        sum += pow(i, k)
    return sum


if __name__ == '__main__':
    N = 8
    k = 4
    print(int(findSum(N,  k)))
