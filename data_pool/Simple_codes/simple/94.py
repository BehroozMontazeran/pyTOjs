from math import pow, sqrt

def area(r):
    if r < 0:
        return -1
    area = 3.14 * pow(r / (2 * sqrt(2)), 2)
    return area

if __name__ == "__main__":
    a = 5
    print("{:.6f}".format(area(a)))
