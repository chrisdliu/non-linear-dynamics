"""
A module for vector math.
"""


__author__ = 'Christopher Liu'


from .vector import *


def v_zero(dim):
    """
    Returns a zero vector of the provided dimension.

    :type dim: int
    :param dim: dimension
    :rtype: Vector
    :return: a zero vector
    """
    return Vector(*([0] * dim))


v_i = Vector(1, 0, 0)

v_j = Vector(0, 1, 0)

v_k = Vector(0, 0, 1)
