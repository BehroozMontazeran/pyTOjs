b = [0 for i in range(50)]


def PowerArray(n, k):
    count = 0
    while (k):
        if (k % n == 0):
            k //= n
            count += 1
        elif (k % n == 1):
            k -= 1
            b[count] += 1
            if (b[count] > 1):
                print(- 1)
                return 0
        else:
            print(- 1)
            return 0
    for i in range(50):
        if (b[i]):
            print(i,end=",")


if __name__ == '__main__':
    N = 3
    K = 40
    PowerArray(N,  K)
