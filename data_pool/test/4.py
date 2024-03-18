
import math


def findCoprimePair(N):
    for x in range(2,  int(math.sqrt(N)) + 1):
        if (N % x == 0):
            while (N % x == 0):
                N //= x
            if (N > 1):
                print(x,     N)
                return
    print("-1")


N = 45
findCoprimePair(N)
N = 25
findCoprimePair(N)
