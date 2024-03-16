from math import sqrt, floor, ceil


def is_rtol(s):
    tmp = floor(sqrt(len(s))) - 1
    first = s[tmp]
    for pos in range(tmp,  len(s) - 1,  tmp):
        if (s[pos] != first):
            return False
    return True


if __name__ == '__main__':
    str = "  abcxabxcaxbcxabc  "
    if (is_rtol(str)):
        print("   Yes   ")
    else:
        print("   No   ")
