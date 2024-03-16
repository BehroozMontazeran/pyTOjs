def no_of_ways(s):
    n = len(s)
    count_left = 0
    count_right = 0
    for i in range(0,  n,  1):
        if (s[i] == s[0]):
            count_left += 1
        else:
            break
    i = n - 1
    while (i >= 0):
        if (s[i] == s[n - 1]):
            count_right += 1
        else:
            break
        i -= 1
    if (s[0] == s[n - 1]):
        return ((count_left + 1) * (count_right + 1))
    else:
        return (count_left + count_right + 1)


if __name__ == '__main__':
    s = "geeksforgeeks"
    print(no_of_ways(s))
