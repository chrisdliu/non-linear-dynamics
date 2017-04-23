

__author__ = 'Christopher Liu'


import numpy as np
from math import cos, sin, pi


def veci(*x):
    return np.array(x, dtype=np.int)


def vecf(*x):
    return np.array(x, dtype=np.float)


def zeroi(n):
    return veci([0] * n)


def zerof(n):
    return vecf([0] * n)


def i2():
    return veci(1, 0)


def j2():
    return veci(0, 1)


def i3():
    return veci(1, 0, 0)


def j3():
    return veci(0, 1, 0)


def k3():
    return veci(0, 0, 1)


def h(v):
    return v[:-1]


def mag(v, order=2):
    return np.linalg.norm(v, order)


def norm(v):
    return v / mag(v)


def vi_rotate2(vector, theta, trans=None):
    """
    Inplace 2d rotation
    """
    if len(vector) != 2:
        raise ArithmeticError('Vector must have 2 elements.')
    if trans is not None and len(trans) != 2:
        raise ArithmeticError('Translation vector must have 2 elements.')

    if trans is not None:
        vector -= trans
    vector[:] = m_rotate2(theta) @ vector
    if trans is not None:
        vector += trans

    return vector


def vn_rotate2(vector, theta, trans=None):
    """
    Returns 2d rotation result
    """
    result = vecf(*vector)
    vi_rotate2(result, theta, trans)
    return result


def vi_rotate3(vector, theta, axis, trans=None):
    if len(vector) != 3:
        raise ArithmeticError('Vector must have 3 elements.')
    if len(axis) != 3:
        raise ArithmeticError('Axis vector must have 3 elements.')
    if trans is not None and len(trans) != 3:
        raise ArithmeticError('Translation vector must have 3 elements.')
    
    # normalize axis
    naxis = norm(axis)

    t = theta * pi / 180
    x, y, z = [*vector]
    u, v, w = [*axis]
    if trans is not None:
        a, b, c = [*trans]
    else:
        a, b, c = 0, 0, 0
    ct = cos(t)
    st = sin(t)

    # lmao how does this work
    vector[0] = (a*(v*v+w*w)-u*(b*v+c*w-u*x-v*y-w*z))*(1-ct)+x*ct+(-c*v+b*w-w*y+v*z)*st
    vector[1] = (b*(u*u+w*w)-v*(a*u+c*w-u*x-v*y-w*z))*(1-ct)+y*ct+(c*u-a*w+w*x-u*z)*st
    vector[2] = (c*(u*u+v*v)-w*(a*u+b*v-u*x-v*y-w*z))*(1-ct)+z*ct+(-b*u+a*v-v*x+u*y)*st

    return vector


def vn_rotate3(vector, theta, axis, trans=None):
    result = vecf(*vector)
    vi_rotate3(result, theta, axis, trans)
    return result


def m_scale2(w, h):
    return np.array([[ w,  0],
                     [ 0,  h]])


def m_rotate2(theta):
    t = theta * pi / 180.0
    return np.array([[ cos(t), -sin(t)],
                     [ sin(t),  cos(t)]])
    

def m_trans2(x, y):
    return np.array([[ 1,  0,  x],
                     [ 0,  1,  y],
                     [ 0,  0,  1]])


def mh_scale2(w, h):
    return np.array([[ w,  0,  0],
                     [ 0,  h,  0],
                     [ 0,  0,  1]])


def mh_rotate2(theta):
    t = theta * pi / 180.0
    return np.array([[ cos(t), -sin(t),  0],
                     [ sin(t),  cos(t),  0],
                     [      0,       0,  1]])
