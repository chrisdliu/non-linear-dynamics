'''
sum of digits squared
'''
import math


def getsum(n):
    d = int(math.log10(n)) + 1
    sum = 0
    for i in range(d):
        t = n // (10 ** i)
        sum += (t % 10) ** 2
    return sum


def dynamic(n):
    orbit = [n,]
    next = getsum(n)
    while next not in orbit:
        orbit.append(next)
        next = getsum(orbit[-1])
    orbit.append(next)
    last = orbit[-1]
    print(orbit)

max = 0
for i in range(1, 486):
    if getsum(i) > max:
        print(i)
        max = getsum(i)