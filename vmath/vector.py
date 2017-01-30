from numbers import Number
from math import cos, sin, pi


class Vector:
    def __init__(self, *args):
        """
        Vector initialization.

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

    def __setattr__(self, key, value):
        if 'dim' in self.__dict__ and key is 'dim':
            raise KeyError('Cannot modify a vector\'s dimension!')
        super().__setattr__(key, value)

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
        res = '(' + ', '.join(['{:d}' if isinstance(self[i], int) else '{:.2f}' for i in range(len(self))]) + ')'
        return res.format(*self._data)

    def __repr__(self):
        return 'Vector' + str(self)

    def rotate(self, trans, axis, theta):
        """
        Rotates the vector around an axis by theta degrees

        :type trans: Vector
        :param trans: A point the axis passes through
        :type axis: Vector
        :param axis: Direction of axis (if not normalized, it will be normalized in calculation)
        :type theta: float
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
