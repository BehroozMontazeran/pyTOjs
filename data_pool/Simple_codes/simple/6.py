def printhexaRec(n):
    if (n == 0 or n == 1 or n == 2 or n == 3 or n == 4 or n == 5):
        return 0
    elif (n == 6):
        return 1
    else:
        return (
            printhexaRec(
                n -
                1) +
            printhexaRec(
                n -
                2) +
            printhexaRec(
                n -
                3) +
            printhexaRec(
                n -
                4) +
            printhexaRec(
                n -
                5) +
            printhexaRec(
                n -
                6))


def printhexa(n):
    print(printhexaRec(n))


n = 11
printhexa(n)
