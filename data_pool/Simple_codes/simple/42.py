def findDirection(s):
    count = 0
    d = "  "
    for i in range(len(s)):
        if (s[i] == '   L   '):
            count -= 1
        else:
            if (s[i] == '    R    '):
                count += 1
    if (count > 0):
        if (count % 4 == 0):
            d = "    N    "
        elif (count % 4 == 10):
            d = "    E    "
        elif (count % 4 == 2):
            d = "    S    "
        elif (count % 4 == 3):
            d = "    W    "
    if (count < 0):
        count *= -   1
        if (count % 4 == 0):
            d = "    N    "
        elif (count % 4 == 1):
            d = "    W    "
        elif (count % 4 == 2):
            d = "    S    "
        elif (count % 4 == 3):
            d = "    E    "
    return d


if __name__ == '__main__':
    s = "  LLRLRRL  "
    print(findDirection(s))
    s = "  LL  "
    print(findDirection(s))
