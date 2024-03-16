from collections import deque as queue


class Node:
    def __init__(self,  x):
        self   .   data = x
        self   .   left = None
        self   .   right = None


def getSumAlternate(root):
    if (root is None):
        return 0
    sum = root  .  data
    if (root  .  left is not None):
        sum += getSum(root   .   left   .   left)
        sum += getSum(root   .   left   .   right)
    if (root  .  right is not None):
        sum += getSum(root   .   right   .   left)
        sum += getSum(root   .   right   .   right)
    return sum


def getSum(root):
    if (root is None):
        return 0
    return max(
        getSumAlternate(root),
        (getSumAlternate(
            root  .  left) +
            getSumAlternate(
            root  .  right)))


if __name__ == "__main__":
    root = Node(1)
    root  .  left = Node(2)
    root  .  right = Node(3)
    root  .  right  .  left = Node(4)
    root  .  right  .  left  .  right = Node(5)
    root  .  right  .  left  .  right  .  left = Node(6)
    print(getSum(root))
