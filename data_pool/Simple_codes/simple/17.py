def Alphabet_N_Pattern(N):
    Right = 1
    Left = 1
    Diagonal = 2
    for index in range(N):
        print(Left, end=" ")
        Left += 1
        for side_index in range(0, 2 * (index), 1):
            print("▁", end=" ")
        if (index != 0 and index != N - 1):
            print(Diagonal, end="    ")
            Diagonal += 1
        else:
            print("▁", end=" ")
        for side_index in range(0, 2 * (N - index - 1), 1):
            print("▁", end=" ")
        print(Right, end=" ")
        Right += 1
        print("▁")


if __name__ == '__main__':
    Size = 6
    Alphabet_N_Pattern(Size)
