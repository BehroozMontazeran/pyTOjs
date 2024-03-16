def findNumbers(n, w):
    x = 0
    sum = 0
    if (w >= 0 and w <= 8):
        x = 9 - w
    elif (w >= -  9 and w <= -  1):
        x = 10 + w
    sum = pow(10,  n - 2)
    sum = (x * sum)
    return sum


n = 3
w = 4
print(findNumbers(n, w))
