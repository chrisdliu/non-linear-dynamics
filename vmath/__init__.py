"""
A package for vector math.
"""


__author__ = 'Christopher Liu'


from .vmath import *


def v_zero(dim):
    """
    Returns a zero vector of the provided dimension.

    :type dim: int
    :param dim: dimension
    :rtype: Vector
    :return: a zero vector
    """
    return Vector(*([0] * dim))


def v_i():
    """
    Returns a unit vector along the x axis in 3 dimensions.

    :rtype: Vector
    :return: unit vector i
    """
    return Vector(1, 0, 0)


def v_j():
    """
    Returns a unit vector along the y axis in 3 dimensions.

    :rtype: Vector
    :return: unit vector j
    """
    return Vector(0, 1, 0)


def v_k():
    """
    Returns a unit vector along the z axis in 3 dimensions.

    :rtype: Vector
    :return: unit vector k
    """
    return Vector(0, 0, 1)