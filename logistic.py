import math

def dynamic(a, x, i):
    if i <= 1:
        return a*x*(1-x)
    else:
        nx = dynamic(a, x, i-1)
        print(nx)
        return a*nx*(1-nx)

dynamic(3.25, .3, 100)