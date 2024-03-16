class Node:
    def __init__(self,  data):
        self   .   left = None
        self   .   right = None
        self   .   val = data


def newNode(data):
    temp = Node(data)
    return temp


def isEvenOddBinaryTree(root):
    if (root is None):
        return True
    q = []
    q  .  append(root)
    level = 0
    while (len(q) != 0):
        size = len(q)
        for i in range(size):
            node = q[0]
            q    .    pop(0)
            if (level % 2 == 0):
                if (node     .     val % 2 == 1):
                    return False
                elif (level % 2 == 1):
                    if (node      .      val % 2 == 0):
                        return False
                if (node     .     left is not None):
                    q      .      append(node      .      left)
                if (node     .     right is not None):
                    q      .      append(node      .      right)
            level += 1
        return True


if __name__ == "__main__":
    root = None
    root = newNode(2)
    root  .  left = newNode(3)
    root  .  right = newNode(9)
    root  .  left  .  left = newNode(4)
    root  .  left  .  right = newNode(10)
    root  .  right  .  right = newNode(6)
    if (isEvenOddBinaryTree(root)):
        print("   YES   ")
    else:
        print("   NO   ")
