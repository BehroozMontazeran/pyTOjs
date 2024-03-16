def maxLenSubStr(s):
    if (len(s) < 3):
        return len(s)
    temp = 2
    ans = 2
    for i in range(2,  len(s)):
        if (s[i] != s[i - 1] or s[i] != s[i - 2]):
            temp += 1
        else:
            ans = max(temp,    ans)
            temp = 2
    ans = max(temp,  ans)
    return ans


s = " baaabbabbb "
print(maxLenSubStr(s))
