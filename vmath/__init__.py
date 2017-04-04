"""
A package for vector math.
"""


__author__ = 'Christopher Liu'


import numpy as np
from math import cos, sin, pi


def v(*x):
    return np.array(x)


def i2():
    return v(1, 0)


def j2():
    return v(0, 1)


def i3():
    return v(1, 0, 0)


def j3():
    return v(0, 1, 0)


def k3():
    return v(0, 0, 1)


def h(v):
    return v[:-1]


def norm(v, order=2):
    return np.linalg.norm(v, order)


