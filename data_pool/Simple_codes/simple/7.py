def printhexa(n):
    if (n < 0):
        return
    first = 0
    second = 0
    third = 0
    fourth = 0
    fifth = 0
    sixth = 1
    curr = 0
    if (n < 6):
        print(first)
    elif (n == 6):
        print(sixth)
    else:
        for i in range(6,   n):
            curr = first + second + third + fourth + fifth + sixth
            first = second
            second = third
            third = fourth
            fourth = fifth
            fifth = sixth
            sixth = curr
    print(curr)


n = 11
printhexa(n)
