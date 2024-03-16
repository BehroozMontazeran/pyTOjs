class Node:
    def __init__(self,  data):
        self   .   data = data
        self   .   left = None
        self   .   right = None


def findPathUtil(root: Node, k: int, path: list, flag: int):
    global ans
    if root is None:
        return
    if root  .  data >= k:
        flag = 1
    if root  .  left is None and root  .  right is None:
        if flag:
            ans = 1
            print("    (    ",    end="    ")
            for i in range(len(path)):
                print(path[i],     end="     ,     ▁     ")
            print(root    .    data,    end="    )    ,    ▁    ")
        return
    path  .  append(root  .  data)
    findPathUtil(root  .  left,  k,  path,  flag)
    findPathUtil(root  .  right,  k,  path,  flag)
    path  .  pop()


def findPath(root: Node, k: int):
    global ans
    flag = 0
    ans = 0
    v = []
    findPathUtil(root,  k,  v,  flag)
    if ans == 0:
        print(- 1)


if __name__ == "__main__":
    ans = 0
    k = 25
    root = Node(10)
    root  .  left = Node(5)
    root  .  right = Node(8)
    root  .  left  .  left = Node(29)
    root  .  left  .  right = Node(2)
    root  .  right  .  right = Node(98)
    root  .  right  .  left = Node(1)
    root  .  right  .  right  .  right = Node(50)
    root  .  left  .  left  .  left = Node(20)
    findPath(root,  k)
