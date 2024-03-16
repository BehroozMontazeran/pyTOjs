def maxSum(str):
    maximumSum = 0
    totalOnes = 0
    for i in str:
        if i == '1':
            totalOnes += 1
    zero = 0
    ones = 0
    i = 0
    while i < len(str):
        if (str[i] == '0'):
            zero += 1
        else:
            ones += 1
        maximumSum = max(maximumSum,   zero + (totalOnes - ones))
        i += 1
    return maximumSum


if __name__ == '__main__':
    str = "011101"
    print(maxSum(str))
