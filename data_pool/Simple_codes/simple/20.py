def nextGreater(N):
    power_of_2 = 1
    shift_count = 0
    while (True):
        if (((N >> shift_count) & 1) % 2 == 0):
            break
        shift_count += 1
        power_of_2 = power_of_2 * 2
    return (N + power_of_2)


N = 11
print(" The ▁ next ▁ number ▁ is ▁ = ", nextGreater(N))
