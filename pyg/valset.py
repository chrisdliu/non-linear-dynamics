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
    def incr(self):
        self.value += 1

    def decr(self):
        self.value -= 1


class BoolValue(ValueObj):
    def __init__(self, value):
        assert type(value) is bool, 'Value is not a bool!'
        super().__init__(value)

    def toggle(self):
        self.value = not self.value


class ValSet:
    def __init__(self):
        self.vals = {}

    def add_num_value(self, name, value):
        self.vals[name] = NumValue(value)

    def add_bool_value(self, name, value):
        self.vals[name] = BoolValue(value)

    def get_valobj(self, name):
        return self.vals[name]

    def get_val(self, name):
        return self.vals[name].value

    def set_val(self, name, value):
        self.vals[name].value = value

