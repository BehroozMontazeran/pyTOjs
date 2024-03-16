def FlipBits(n):
    n -= (n & (- n))
    return n


if __name__ == '__main__':
    N = 12
    print("  The  ▁  number  ▁  after  ▁  unsetting  ▁  the  ",  end="  ")
    print("  ▁  rightmost  ▁  set  ▁  bit  :  ▁  ",  FlipBits(N))
