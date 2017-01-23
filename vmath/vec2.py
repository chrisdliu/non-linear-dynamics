import numbers


class Vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        if not isinstance(other, numbers.Number):
            raise ArithmeticError('Can\'t multiply by a non-number!')
        return Vec2(self.x * other, self.y * other)

    def __floordiv__(self, other):
        if not isinstance(other, numbers.Number):
            raise ArithmeticError('Can\'t divide by a non-number!')
        return Vec2(self.x // other, self.y // other)

    def __truediv__(self, other):
        if not isinstance(other, numbers.Number):
            raise ArithmeticError('Can\'t divide by a non-number!')
        return Vec2(self.x / other, self.y / other)

    def __neg__(self):
        return Vec2(-self.x, -self.y)

    def __abs__(self):
        return (self.x ** 2 + self.y ** 2) ** .5

    def __bool__(self):
        return self.x != 0 or self.y != 0

    def __lt__(self, other):
        return abs(self) < abs(other)

    def __le__(self, other):
        return abs(self) <= abs(other)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return self.x != other.x or self.y != other.y

    def __ge__(self, other):
        return abs(self) >= abs(other)

    def __gt__(self, other):
        return abs(self) > abs(other)

    def __getitem__(self, item):
        if item < 0 or item > 1:
            raise IndexError
        if item == 0:
            return self.x
        else:
            return self.y

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        if self.n < 2:
            result = self[self.n]
            self.n += 1
            return result
        else:
            raise StopIteration

    def __str__(self):
        return '(%.3f, %.3f)' % (self.x, self.y)

    def __repr__(self):
        return str(self)
