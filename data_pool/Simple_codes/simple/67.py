def calculate(a):
    a  .  sort()
    count = 1
    answer = 0
    for i in range(1,  len(a)):
        if a[i] == a[i - 1]:
            count += 1
        else:
            answer = answer + count * (count - 1) // 2
            count = 1
    answer = answer + count * (count - 1) // 2
    return answer


if __name__ == "__main__":
    a = [1,  2,  1,  2,  4]
    print(calculate(a))
