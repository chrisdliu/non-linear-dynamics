"""
Defines value objects (Value) and value sets (ValSet) for accessing variables between gui components.
"""


class Value(object):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def set_val(self, new_value):
        if self.is_valid(new_value):
            self.value = new_value

    def set_val_cast(self, new_value):
        parsed_value = self.parse(new_value)
        if parsed_value is not None:
            self.set_val(parsed_value)

    def parse(self, new_value_cast):
        return None

    def is_valid(self, new_value):
        return True


class NumberValue(Value):
    def __init__(self, value, limit='', inclusive='ul', low=0, high=1):
        super().__init__(value)
        self.limit = limit
        self.inclusive = inclusive
        self.low = low
        self.high = high
        assert self.is_valid(value), 'Invalid default %s!' % str(self.__class__)

    def incr(self):
        self.set_val(self.value + 1)

    def decr(self):
        self.set_val(self.value - 1)

    def is_valid(self, new_value):
        if 'l' in self.limit:
            if 'l' in self.inclusive:
                if new_value < self.low:
                    return False
            else:
                if new_value <= self.low:
                    return False
        if 'u' in self.limit:
            if 'u' in self.inclusive:
                if new_value > self.high:
                    return False
            else:
                if new_value >= self.high:
                    return False
        return True


class FloatValue(NumberValue):
    def __str__(self):
        return '%.5f' % self.value

    def parse(self, new_value_cast):
        try:
            return float(new_value_cast)
        except ValueError:
            return None


class IntValue(NumberValue):
    def __str__(self):
        return '%i' % self.value

    def parse(self, new_value_cast):
        try:
            return int(new_value_cast)
        except ValueError:
            return None

    def is_valid(self, new_value):
        if new_value % 1 != 0:
            return False
        return super().is_valid(new_value)


class ComplexValue(NumberValue):
    def __str__(self):
        return '%.3f + %.3fj' % (self.value.real, self.value.imag)

    def parse(self, new_value_cast):
        try:
            return complex(new_value_cast)
        except ValueError:
            return None


class BoolValue(Value):
    def toggle(self):
        self.value = not self.value

    def parse(self, new_value_cast):
        try:
            return bool(new_value_cast)
        except ValueError:
            return None

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
        self.vals[name].set_val(value)
