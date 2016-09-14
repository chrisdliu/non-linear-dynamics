import math


def dynamic(a, x, i, start=0):
    print('s: ' + str(x))
    for n in range(i):
        x = a*x*(1-x)
        if start < n + 1:
            print(x)


dynamic(4, 0.6, 200, 0)

'''
intersection always a fixed point
3.25  -> (0.812, 0.495)
3.5   -> (0.875, 0.383, 0.827, 0.501)
3.555 -> (0.372, 0.831, 0.500, 0.889, 0.351, 0.810, 0.546, 0.881)
4     -> (random???)

'''