class ValueObj:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def set_val(self, new_value):
        if self.is_valid(new_value):
            self.value = new_value

    def is_valid(self, new_value):
        return True


class NumValue(ValueObj):
    def __init__(self, value, limit='', inclusive='ul', low=0, high=1):
        super().__init__(value)
        self.limit = limit
        self.inclusive = inclusive
        self.low = low
        self.high = high
        assert self.is_valid(value), 'Invalid %s!' % str(self.__class__)

    def incr(self):
        self.value += 1

    def decr(self):
        self.value -= 1

    def is_valid(self, new_value):
        if 'l' in self.limit:
            if 'l' in self.inclusive:
                if self.low > new_value:
                    return False
            else:
                if self.low >= new_value:
                    return False
        if 'u' in self.limit:
            if 'u' in self.inclusive:
                if new_value > self.high:
                    return False
            else:
                if new_value >= self.high:
                    return False
        return True


class FloatValue(NumValue):
    def __str__(self):
        return '%.5f' % self.value


class IntValue(NumValue):
    def __str__(self):
        return '%i' % self.value

    def is_valid(self, new_value):
        if new_value % 1 != 0:
            return False
        return super().is_valid(new_value)


class ComplexValue(NumValue):
    def __str__(self):
        return '%.3f + %.3fj' % (self.value.real, self.value.imag)


class BoolValue(ValueObj):
    def toggle(self):
        self.value = not self.value

    def is_valid(self, new_value):
        return type(new_value) == bool


class ValSet:
    def __init__(self):
        self.vals = {}

    def add_float_value(self, name, value, limit='', inclusive='ul', low=0, high=1):
        self.vals[name] = FloatValue(value, limit, inclusive, low, high)

    def add_int_value(self, name, value, limit='', inclusive='ul', low=0, high=1):
        self.vals[name] = IntValue(value, limit, inclusive, low, high)

    def add_complex_value(self, name, value, limit='', inclusive='ul', low=0, high=1):
        self.vals[name] = ComplexValue(value, limit, inclusive, low, high)

    def add_bool_value(self, name, value):
        self.vals[name] = BoolValue(value)

    def get_valobj(self, name):
        return self.vals[name]

    def get_val(self, name):
        return self.vals[name].value

    def set_val(self, name, value):
        self.vals[name].value = value

