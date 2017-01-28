import numbers
from math import cos, sin, pi


class Vector:
    def __init__(self, *args):
        if not args:
            raise TypeError('Must supply arguments!')
        for x in args:
            if not isinstance(x, numbers.Number):
                raise TypeError('All arguments must be numbers!')
        self._data = list(args)
        self.dim = len(args)

    def __add__(self, other):
        if isinstance(other, Vector):
            if self.dim is not other.dim:
                raise ArithmeticError('Vectors must be same dimension!')
            return Vector(*[self[i] + other[i] for i in range(len(self))])
        elif isinstance(other, numbers.Number):
            return Vector(*[self[i] + other for i in self])
        else:
            raise TypeError('Must add by a number or a vector!')

    def __sub__(self, other):
        if isinstance(other, Vector):
            if self.dim is not other.dim:
                raise ArithmeticError('Vectors must be same dimension!')
            return Vector(*[self[i] - other[i] for i in range(len(self))])
        elif isinstance(other, numbers.Number):
            return Vector(*[self[i] + other for i in self])
        else:
            raise TypeError('Must subtract by a number or a vector!')

    def __mul__(self, other):
        if isinstance(other, Vector):
            if self.dim is not other.dim:
                raise ArithmeticError('Vectors must be same dimension!')
            return sum([self[i] * other[i] for i in range(len(self))])
        elif isinstance(other, numbers.Number):
            return Vector(*[x * other for x in self])
        else:
            raise TypeError('Must multiply by a number or a vector!')

    def __matmul__(self, other):
        if isinstance(other, Vector):
            if self.dim != 3 or other.dim != 3:
                raise ArithmeticError('Vectors must have dimension 3!')
        x1 = self[1] * other[2] - self[2] * other[1]
        x2 = -(self[0] * other[2] - self[2] * other[0])
        x3 = self[0] * other[1] - self[1] * other[0]
        return Vector(x1, x2, x3)

    def __floordiv__(self, other):
        if isinstance(other, numbers.Number):
            return Vector(*[x // other for x in self])
        else:
            raise TypeError('Must divide by a number!')

    def __truediv__(self, other):
        if isinstance(other, numbers.Number):
            return Vector(*[x / other for x in self])
        else:
            raise TypeError('Must divide by a number!')

    def __neg__(self):
        args = []
        for x in self._data:
            args.append(-x)
        return Vector(*args)

    def __invert__(self):
        """
        Normalizes the vector
        """
        mag = abs(self)
        return self / mag

    def get_mag(self, new_mag):
        return ~self * new_mag

    def __abs__(self):
        mag2 = sum([x ** 2 for x in self])
        return mag2 ** .5

    def __bool__(self):
        for x in self._data:
            if x:
                return True
        return False

    def __lt__(self, other):
        if self.dim is not other.dim:
            raise ArithmeticError('Vectors must be same dimension!')
        return abs(self) < abs(other)

    def __le__(self, other):
        if self.dim is not other.dim:
            raise ArithmeticError('Vectors must be same dimension!')
        return abs(self) <= abs(other)

    def __eq__(self, other):
        if self.dim is not other.dim:
            raise ArithmeticError('Vectors must be same dimension!')
        for i in range(self.dim):
            if self[i] != other[i]:
                return False
        return True

    def __ne__(self, other):
        if self.dim is not other.dim:
            raise ArithmeticError('Vectors must be same dimension!')
        for i in range(self.dim):
            if self[i] != other[i]:
                return True
        return False

    def __ge__(self, other):
        if self.dim is not other.dim:
            raise ArithmeticError('Vectors must be same dimension!')
        return abs(self) >= abs(other)

    def __gt__(self, other):
        if self.dim is not other.dim:
            raise ArithmeticError('Vectors must be same dimension!')
        return abs(self) > abs(other)

    def __setattr__(self, key, value):
        if 'dim' in self.__dict__ and key is 'dim':
            raise KeyError('Cannot modify a vector\'s dimension!')
        super().__setattr__(key, value)

    def __getitem__(self, item):
        if item < 0 or item >= self.dim:
            raise IndexError
        return self._data[item]

    def __setitem__(self, key, value):
        if not isinstance(key, int):
            raise KeyError('Key must be an integer!')
        if key < 0 or key >= self.dim:
            raise IndexError
        if not isinstance(value, numbers.Number):
            raise ArithmeticError('Value must be a number!')
        self._data[key] = value

    def __len__(self):
        return self.dim

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        if self.n < self.dim:
            result = self[self.n]
            self.n += 1
            return result
        else:
            raise StopIteration

    def __str__(self):
        res = '(' + '{:.2f}, ' * (self.dim - 1) + '{:.2f})'
        return res.format(*self._data)

    def __repr__(self):
        return str(self)

    def rotate(self, trans, axis, theta):
        """
        Rotates the vector around an axis by theta degrees.
        :param trans: A point the axis passes through
        :param axis: Direction of axis (if not normalized, it will be normalized in calculation)
        :param theta: Rotation amount in degrees
        """
        if self.dim != 3:
            raise ArithmeticError('Vector must have dimension 3!!!')
        if trans.dim != 3:
            raise ArithmeticError('Translation vector must have dimension 3!!!')
        if axis.dim != 3:
            raise ArithmeticError('Axis vector must have dimension 3!!!')
        # normalize axis vector
        if abs(axis) != 1:
            axis = ~axis

        theta *= pi / 180
        x, y, z = [*self]
        a, b, c = [*trans]
        u, v, w = [*axis]

        # lmao how does this work
        self[0] = (a*(v*v+w*w)-u*(b*v+c*w-u*x-v*y-w*z))*(1-cos(theta))+x*cos(theta)+(-c*v+b*w-w*y+v*z)*sin(theta)
        self[1] = (b*(u*u+w*w)-v*(a*u+c*w-u*x-v*y-w*z))*(1-cos(theta))+y*cos(theta)+(c*u-a*w+w*x-u*z)*sin(theta)
        self[2] = (c*(u*u+v*v)-w*(a*u+b*v-u*x-v*y-w*z))*(1-cos(theta))+z*cos(theta)+(-b*u+a*v-v*x+u*y)*sin(theta)


def v_zero(dim):
    return Vector(*([0] * dim))


v_i = Vector(1, 0, 0)
v_j = Vector(0, 1, 0)
v_k = Vector(0, 0, 1)
