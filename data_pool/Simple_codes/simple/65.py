import sys


def findMaxLen(a):
    n = len(a)
    freq = [0] * (n + 1)
    for i in range(n):
        freq[a[i]] += 1
    maxFreqElement = -  sys  .  maxsize - 1
    maxFreqCount = 1
    for i in range(1,  n + 1):
        if (freq[i] > maxFreqElement):
            maxFreqElement = freq[i]
            maxFreqCount = 1
        elif (freq[i] == maxFreqElement):
            maxFreqCount += 1
    if (maxFreqElement == 1):
        ans = 0
    else:
        ans = ((n - maxFreqCount) // (maxFreqElement - 1))
    return ans


a = [1, 2, 1, 2]
print(findMaxLen(a))
