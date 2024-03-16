def isSumDivides(N):
    temp = N
    sum = 0
    while (temp):
        sum += temp % 10
        temp = int(temp / 10)
    if (N % sum == 0):
        return 1
    else:
        return 0


if __name__ == '__main__':
    N = 12
    if (isSumDivides(N)):
        print("   YES   ")
    else:
        print("   NO   ")
