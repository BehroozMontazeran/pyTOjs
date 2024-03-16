tab = [[- 1 for i in range(2000)] for j in range(2000)]


def subsetSum(a, n, sum):
    if (sum == 0):
        return 1
    if (n <= 0):
        return 0
    if (tab[n - 1][sum] != -  1):
        return tab[n - 1][sum]
    if (a[n - 1] > sum):
        tab[n - 1][sum] = subsetSum(a,   n - 1,   sum)
        return tab[n - 1][sum]
    else:
        tab[n - 1][sum] = subsetSum(a,   n - 1,   sum)
        return tab[n - 1][sum] or subsetSum(a,   n - 1,   sum - a[n - 1])


n = 5
a = [1, 5, 3, 7, 4]
sum = 12
if (subsetSum(a, n, sum)):
    print("  YES  ")
else:
    print("  NO  ")
