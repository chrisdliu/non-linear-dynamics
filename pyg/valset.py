class NumValue:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class ValSet:
    def __init__(self):
        self.vals = {}

    def add_value(self, name, value):
        self.vals[name] = NumValue(value)

    def get_obj(self, name):
        return self.vals[name]

    def get_val(self, name):
        return self.vals[name].value