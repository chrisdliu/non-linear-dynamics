from numbers import Number
from math import cos, sin, pi


__all__ = ['Vector', 'Matrix']


class Vector:
    def __init__(self, *args):
        """
        Vector constructor.

        >>> a = Vector(1, 2, 3)
        >>> b = Vector(1+2j, 4-6j)
        >>> print(a)
        (1, 2, 3)
        >>> print(b)
        (1.00+2.00j, 4.00-6.00j)

        :param args: a list of numbers
        """
        if not args:
            raise TypeError('Must supply arguments!')
        for x in args:
            if not isinstance(x, Number):
                raise TypeError('All arguments must be numbers!')
        self._data = list(args)
        self.dim = len(args)

    def __add__(self, other):
        """
        If added by a vector, performs vector addition.
        If added by a number, performs scalar addition.

        >>> a = Vector(1, 2)
        >>> b = Vector(2, 4)
        >>> c = 5
        >>> print(a + b)
        (3, 6)
        >>> print(a + c)
        (6, 7)
        """

        if isinstance(other, Vector):
            if self.dim is not other.dim:
                raise ArithmeticError('Vectors must be same dimension!')
            return Vector(*[self[i] + other[i] for i in range(len(self))])
        elif isinstance(other, Number):
            return Vector(*[self[i] + other for i in self])
        else:
            raise TypeError('Must add by a number or a vector!')

    def __sub__(self, other):
        """
        If subtracted by a vector, performs vector subtraction.
        If subtracted by a number, performs scalar subtraction.

        >>> a = Vector(1, 2)
        >>> b = Vector(2, 4)
        >>> c = 5
        >>> print(a - b)
        (-1, -2)
        >>> print(a - c)
        (-4, -3)
        """
        if isinstance(other, Vector):
            if self.dim is not other.dim:
                raise ArithmeticError('Vectors must be same dimension!')
            return Vector(*[self[i] - other[i] for i in range(len(self))])
        elif isinstance(other, Number):
            return Vector(*[self[i] + other for i in self])
        else:
            raise TypeError('Must subtract by a number or a vector!')

    def __mul__(self, other):
        """
        If multiplied by a vector, performs a dot product.
        If multiplied by a number, performs scalar multiplication.

        >>> a = Vector(1, 2)
        >>> b = Vector(2, 4)
        >>> c = 3
        >>> print(a * b)
        10
        >>> print(a * c)
        (3, 6)
        """
        if isinstance(other, Vector):
            if self.dim is not other.dim:
                raise ArithmeticError('Vectors must be same dimension!')
            return sum([self[i] * other[i] for i in range(len(self))])
        elif isinstance(other, Number):
            return Vector(*[x * other for x in self])
        else:
            raise TypeError('Must multiply by a number or a vector!')

    def __matmul__(self, other):
        """
        Performs a cross product.
        Must multiply by a vector.
        Vectors must have dimension 3.

        >>> a = Vector(1, 2, 3)
        >>> b = Vector(2, 4, -5)
        >>> print(a @ b)
        (-22, 11, 0)
        """
        if isinstance(other, Vector):
            if self.dim != 3 or other.dim != 3:
                raise ArithmeticError('Vectors must have dimension 3!')
        x1 = self[1] * other[2] - self[2] * other[1]
        x2 = -(self[0] * other[2] - self[2] * other[0])
        x3 = self[0] * other[1] - self[1] * other[0]
        return Vector(x1, x2, x3)

    def __rmul__(self, other):
        if not isinstance(other, Matrix):
            raise TypeError('Must multiply by a matrix on the left!')
        if other.dim[1] != self.dim:
            raise ArithmeticError('Matrix columns must match vector dimension!')
        return Vector(*[sum([other[x, y] * self[y] for y in range(self.dim)]) for x in range(other.dim[0])])

    def __floordiv__(self, other):
        """
        Performs scalar floor division.
        Must divide by a number.

        >>> a = Vector(3, 8)
        >>> c = 5
        >>> print(a // c)
        (0, 1)
        """
        if isinstance(other, Number):
            return Vector(*[x // other for x in self])
        else:
            raise TypeError('Must divide by a number!')

    def __truediv__(self, other):
        """
        Performs scalar true division.
        Must divide by a number.

        >>> a = Vector(3, 8)
        >>> c = 5
        >>> print(a / c)
        (0.60, 1.60)
        """
        if isinstance(other, Number):
            return Vector(*[x / other for x in self])
        else:
            raise TypeError('Must divide by a number!')

    def __neg__(self):
        """
        Identical to multiplying by -1.

        >>> a = Vector(1, 2)
        >>> print(-a)
        (-1, -2)
        """
        args = []
        for x in self._data:
            args.append(-x)
        return Vector(*args)

    def __invert__(self):
        """
        Normalization.
        Divides the vector by its magnitude.

        >>> a = Vector(1, 2)
        >>> print(~a)
        (0.45, 0.89)
        >>> print(abs(~a))
        1.0
        """
        mag = abs(self)
        return self / mag

    def __abs__(self):
        """
        Returns the magnitude of the vector.

        >>> a = Vector(3, 4)
        >>> print(abs(a))
        5.0
        """
        mag2 = sum([x ** 2 for x in self])
        return mag2 ** .5

    def __bool__(self):
        """
        Returns False if it is the zero vector, True otherwise.

        >>> a = Vector(1, 2)
        >>> True if a else False
        True
        >>> b = Vector(0, 0)
        >>> True if b else False
        False
        """
        for x in self._data:
            if x:
                return True
        return False

    def __lt__(self, other):
        """
        Returns abs(self) < abs(other).

        >>> a = Vector(1, 2)
        >>> b = Vector(2, 4)
        >>> a < b
        True
        """
        if self.dim is not other.dim:
            raise ArithmeticError('Vectors must be same dimension!')
        return abs(self) < abs(other)

    def __le__(self, other):
        """
        Returns abs(self) <= abs(other).

        >>> a = Vector(1, 2)
        >>> b = Vector(2, 4)
        >>> a <= b
        True
        """
        if self.dim is not other.dim:
            raise ArithmeticError('Vectors must be same dimension!')
        return abs(self) <= abs(other)

    def __eq__(self, other):
        """
        Returns True if the vectors are equal, False otherwise.

        >>> a = Vector(1, 2)
        >>> b = Vector(2, 4)
        >>> a == b
        False
        """
        if self.dim is not other.dim:
            raise ArithmeticError('Vectors must be same dimension!')
        for i in range(self.dim):
            if self[i] != other[i]:
                return False
        return True

    def __ne__(self, other):
        """
        Returns True if the vectors are not equal, False otherwise.

        >>> a = Vector(1, 2)
        >>> b = Vector(2, 4)
        >>> a != b
        True
        """
        if self.dim is not other.dim:
            raise ArithmeticError('Vectors must be same dimension!')
        for i in range(self.dim):
            if self[i] != other[i]:
                return True
        return False

    def __ge__(self, other):
        """
        Returns abs(self) >= abs(other).

        >>> a = Vector(1, 2)
        >>> b = Vector(2, 4)
        >>> a >= b
        False
        """
        if self.dim is not other.dim:
            raise ArithmeticError('Vectors must be same dimension!')
        return abs(self) >= abs(other)

    def __gt__(self, other):
        """
        Returns abs(self) > abs(other).

        >>> a = Vector(1, 2)
        >>> b = Vector(2, 4)
        >>> a > b
        False
        """
        if self.dim is not other.dim:
            raise ArithmeticError('Vectors must be same dimension!')
        return abs(self) > abs(other)

    def __getitem__(self, item):
        """
        Returns the number at a given index.

        >>> a = Vector(1, 2, 3)
        >>> a[0]
        1
        >>> a[:2]
        [1, 2]
        """
        if isinstance(item, (int, slice)):
            return self._data[item]
        else:
            raise TypeError('Item must be an integer or slice!')

    def __setitem__(self, key, value):
        """
        Sets the number at a given index.

        >>> a = Vector(1, 2)
        >>> a[0] = 3
        >>> print(a)
        (3, 2)
        """
        if not isinstance(key, int):
            raise KeyError('Key must be an integer!')
        if key < 0 or key >= self.dim:
            raise IndexError
        if not isinstance(value, Number):
            raise ArithmeticError('Value must be a number!')
        self._data[key] = value

    def __len__(self):
        """
        Returns the vector's dimension.
        
        >>> a = Vector(1, 2)
        >>> print(len(a))
        2
        """
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
        form = '(' + ', '.join(['{:d}' if isinstance(self[i], int) else '{:.2f}' for i in range(len(self))]) + ')'
        return form.format(*self._data)

    def __repr__(self):
        return 'Vector' + str(self)

    def __setattr__(self, key, value):
        if 'dim' in self.__dict__ and key is 'dim':
            raise KeyError('Cannot modify a vector\'s dimension!')
        super().__setattr__(key, value)

    def rotate2d(self, theta, trans=None):
        """
        Rotates a 2d vector around a point by theta degrees

        :type theta: float
        :param theta: rotation amount in degrees
        :type trans: Vector(2d)
        :param trans: the point of rotation
        """
        if self.dim != 2:
            raise ArithmeticError('Vector must have dimension 2!!!')
        if trans is not None and trans.dim != 2:
            raise ArithmeticError('Translation vector must have dimension 2!!!')

        theta *= pi / 180
        st = sin(theta)
        ct = cos(theta)
        if trans:
            self.__sub__(trans)
        self[0], self[1] = [*(Matrix([ct, -st], [st, ct]) * self)]
        if trans:
            self.__add__(trans)

        return self

    def rotate3d(self, theta, axis, trans=None):
        """
        Rotates a 3d vector around an axis by theta degrees

        :type theta: float
        :param theta: rotation amount in degrees
        :type axis: Vector(3d)
        :param axis: direction of axis (if not normalized, it will be normalized in calculation)
        :type trans: Vector(3d)
        :param trans: a point on the axis
        """
        if self.dim != 3:
            raise ArithmeticError('Vector must have dimension 3!!!')
        if axis.dim != 3:
            raise ArithmeticError('Axis vector must have dimension 3!!!')
        if trans is not None and trans.dim != 3:
            raise ArithmeticError('Translation vector must have dimension 3!!!')
        # normalize axis vector
        if abs(axis) != 1:
            axis = ~axis

        theta *= pi / 180
        x, y, z = [*self]
        if trans:
            a, b, c = [*trans]
        else:
            a, b, c = 0, 0, 0
        u, v, w = [*axis]
        cost = cos(theta)
        sint = sin(theta)

        # lmao how does this work
        self[0] = (a*(v*v+w*w)-u*(b*v+c*w-u*x-v*y-w*z))*(1-cost)+x*cost+(-c*v+b*w-w*y+v*z)*sint
        self[1] = (b*(u*u+w*w)-v*(a*u+c*w-u*x-v*y-w*z))*(1-cost)+y*cost+(c*u-a*w+w*x-u*z)*sint
        self[2] = (c*(u*u+v*v)-w*(a*u+b*v-u*x-v*y-w*z))*(1-cost)+z*cost+(-b*u+a*v-v*x+u*y)*sint

        return self


class Matrix:
    def __init__(self, *args):
        if not args:
            raise TypeError('Must supply arguments!')
        for row in args:
            if not isinstance(row, (list, tuple, Vector)):
                raise TypeError('All arguments must be lists, tuples, or vectors!')
            for x in row:
                if not isinstance(x, Number):
                    raise TypeError('All elements in arguments must be numbers!')
        for i in range(1, len(args)):
            if len(args[i - 1]) != len(args[i]):
                raise IndexError('All arguments must have the same length!')

        data = [list(row) for row in args]
        self._data = data
        self.dim = (len(data), len(data[0]))

    def __mul__(self, other):
        if isinstance(other, Vector):
            return NotImplemented
        if not isinstance(other, (Number, Matrix)):
            raise TypeError('Must multiply by a number or matrix!')
        if isinstance(other, Number):
            return Matrix(*[[self[x, y] * other for y in range(self.dim[1])] for x in range(self.dim[0])])

    def __getitem__(self, item):
        """
        :type item: int, list(int * 2), tuple(int * 2)
        :rtype: list(Number * dim[1]), int
        """
        if isinstance(item, int):
            return self._data[item]
        elif isinstance(item, (list, tuple)) and len(item) == 2 and isinstance(item[0], int) and isinstance(item[1], int):
            return self._data[item[0]][item[1]]
        else:
            raise IndexError('Index must be an int or a tuple of 2 ints!')

    def __setitem__(self, key, value):
        if not isinstance(key, (list, tuple)):
            raise KeyError('Key must be a list or tuple!')
        if len(key) != 2:
            raise KeyError('Key must have length 2!')
        if key[0] < 0 or key[0] >= self.dim[0] or key[1] < 0 or key[1] >= self.dim[1]:
            raise IndexError
        if not isinstance(value, Number):
            raise ArithmeticError('Value must be a number!')
        self._data[key[0]][key[1]] = value

    def __len__(self):
        """
        Returns the number of rows.
        """
        return self.dim[0]

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        if self.n < self.dim[0]:
            result = self[self.n]
            self.n += 1
            return result
        else:
            raise StopIteration

    def __setattr__(self, key, value):
        if 'dim' in self.__dict__ and key is 'dim':
            raise KeyError('Cannot modify a matrix\'s dimensions!')
        super().__setattr__(key, value)
