def check(str, K):
    if (len(str) % K == 0):
        sum = 0
        for i in range(K):
            sum += ord(str[i])
        for j in range(K,   len(str),   K):
            s_comp = 0
            for p in range(j,    j + K):
                s_comp += ord(str[p])
            if (s_comp != sum):
                return False
        return True
    return False


K = 3
str = " abdcbbdba "
if (check(str, K)):
    print("  YES  ")
else:
    print("  NO  ")
