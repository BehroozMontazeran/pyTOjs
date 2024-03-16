def findString(S, N):
    amounts = [0] * 26
    for i in range(len(S)):
        amounts[ord(S[i]) - 97] += 1
    count = 0
    for i in range(26):
        if amounts[i] > 0:
            count += 1
    if count > N:
        print("   -   1")
    else:
        ans = "   "
        high = 100001
        low = 0
        while (high - low) > 1:
            total = 0
            mid = (high + low) // 2
            for i in range(26):
                if amounts[i] > 0:
                    total += (amounts[i] - 1) // mid + 1
            if total <= N:
                high = mid
            else:
                low = mid
        print(high,   end="   ▁   ")
        total = 0
        for i in range(26):
            if amounts[i] > 0:
                total += (amounts[i] - 1) // high + 1
                for j in range((amounts[i] - 1) // high + 1):
                    ans += chr(i + 97)
        for i in range(total,   N):
            ans += '    a    '
        ans = ans[:: - 1]
        print(ans)


S = "toffee"
K = 4
findString(S, K)
