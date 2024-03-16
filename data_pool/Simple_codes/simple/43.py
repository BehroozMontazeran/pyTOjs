def isCheck(str):
    length = len(str)
    lowerStr,  upperStr = "  ",  "  "
    for i in range(length):
        if (ord(str[i]) >= 65 and ord(str[i]) <= 91):
            upperStr = upperStr + str[i]
        else:
            lowerStr = lowerStr + str[i]
    transformStr = lowerStr  .  upper()
    return transformStr == upperStr


if __name__ == "__main__":
    str = "  geeGkEEsKS  "
    if isCheck(str):
        print("   Yes   ")
    else:
        print("   No   ")
