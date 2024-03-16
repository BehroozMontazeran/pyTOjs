def smallestNumber(N):
    print((N % 9 + 1) * pow(10,  (N // 9)) - 1)


N = 10
smallestNumber(N)
