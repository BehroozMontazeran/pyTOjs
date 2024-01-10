from numpy import *
from sys import version
import math


def computation_function():
    if int(version[0]) > 2:  # Python 3 uses input, not raw_input
        raw_input = input
    name = raw_input('Key in your name: ')  # raw_input strings
    print("Hi", name)
    radius = eval(raw_input('Enter a radius: '))  # For numerical values
    print('you entered radius=%8.5f' % radius)  # formatted output
    print('Enter new name and rin file Name.dat')  # raw_input strings
    infile = open('Name.dat', 'r')  # Read from file Name.dat


    for line in infile:
        line = line.split()  # Splits components of line
        name = line[0]  # First entry in the list
        print("Hi %10s" % (name))  # print Hi + first entry
        r = float(line[1])  # convert string to float
        print("r = %13.5f" % (r))  # convert to float & print
        infile.close()

    A = math.pi * r**2
    print("Done, look in A.dat\n")

    outfile = open('A.dat', 'w')
    outfile.write('r= %13.5f\n' % (r))
    outfile.write('A = %13.5f\n' % (A))
    outfile.close()

    print('r = %13.5f' % (r), ', A = %13.5f' % (A))  # Screen output

    print('\nNow example of integer input')

    age = int(eval(input('Now key in your age as an integer: ')))
    print("age: %4d years old, you don't look it!\n" % (age))

    print("Enter and return a character to finish ")
    s = raw_input()