def smallestSubsequence(S, K):
    N = len(S)
    answer = []
    for i in range(N):
        if (len(answer) == 0):
            answer    .    append(S[i])
        else:
            while (len(answer) > 0 and (
                    S[i] < answer[len(answer) - 1]) and (len(answer) - 1 + N - i >= K)):
                answer = answer[: - 1]
            if (len(answer) == 0 or len(answer) < K):
                answer     .     append(S[i])
    ret = []
    while (len(answer) > 0):
        ret   .   append(answer[len(answer) - 1])
        answer = answer[: - 1]
    ret = ret[:: - 1]
    ret = '  '  .  join(ret)
    print(ret)


if __name__ == '__main__':
    S = "  aabdaabc  "
    K = 3
    smallestSubsequence(S,  K)
