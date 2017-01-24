import numbers


class Vector:
    def __init__(self, *args):
        for x in args:
            if not isinstance(x, numbers.Number):
                raise TypeError('All arguments must be numbers!')
        self._x = list(args)
        self.dim = len(args)

    def __add__(self, other):
        if self.dim is not other.dim:
            raise ArithmeticError('Vectors must be same dimension!')
        args = []
        for i in range(self.dim):
            args.append(self[i] + other[i])
        return Vector(*args)

    def __sub__(self, other):
        if self.dim is not other.dim:
            raise ArithmeticError('Vectors must be same dimension!')
        args = []
        for i in range(self.dim):
            args.append(self[i] - other[i])
        return Vector(*args)

    def __mul__(self, other):
        if not isinstance(other, numbers.Number):
            raise ArithmeticError('Can\'t multiply by a non-number!')
        args = []
        for x in self._x:
            args.append(x * other)
        return Vector(*args)

    def __floordiv__(self, other):
        if not isinstance(other, numbers.Number):
            raise ArithmeticError('Can\'t divide by a non-number!')
        args = []
        for x in self._x:
            args.append(x // other)
        return Vector(*args)

    def __truediv__(self, other):
        if not isinstance(other, numbers.Number):
            raise ArithmeticError('Can\'t divide by a non-number!')
        args = []
        for x in self._x:
            args.append(x / other)
        return Vector(*args)

    def __neg__(self):
        args = []
        for x in self._x:
            args.append(-x)
        return Vector(*args)

    def __abs__(self):
        mag2 = 0
        for x in self._x:
            mag2 += x ** 2
        return mag2 ** .5

    def __bool__(self):
        for x in self._x:
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

    def __getitem__(self, item):
        if item < 0 or item >= self.dim:
            raise IndexError
        return self._x[item]

    def __setitem__(self, key, value):
        if key < 0 or key >= self.dim:
            raise IndexError
        if not isinstance(value, numbers.Number):
            raise ArithmeticError('Value must be a number!')
        self._x[key] = value

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
        res = '(' + '{:.3f}, ' * (self.dim - 1) + '{:.3f})'
        return res.format(*self._x)

    def __repr__(self):
        return str(self)
