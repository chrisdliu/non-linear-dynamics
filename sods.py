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
    return last

count = 0
for x in range(163, 100000):
    last = dynamic(x)
    if last == 1:
        #print(x)
        count += 1

print(count / (100000 - 163))