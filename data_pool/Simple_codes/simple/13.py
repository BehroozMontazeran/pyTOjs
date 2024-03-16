bin = ["000", "001", "010", "011", "100", "101", "110", "111"]


def maxFreq(s):
    binary = "  "
    for i in range(len(s)):
        binary += bin[ord(s[i]) - ord('0')]
    binary = binary[0:  len(binary) - 1]
    count = 1
    prev = -  1
    j = 0
    for i in range(len(binary) - 1,  -  1,  -  1):
        if (binary[i] == '1'):
            count = max(count,    j - prev)
            prev = j
        j += 1
    return count


if __name__ == "__main__":
    octal = "13"
    print(maxFreq(octal))
