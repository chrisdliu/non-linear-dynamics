"""
Defines value objects (Value) and value sets (ValSet) for accessing variables between gui components.
"""


class Value(object):
    """
    Base value class for value objects.

    :var value: the value it holds
    """
    def __init__(self, value):
        """
        Value constructor.

        :param value: the initial value
        """
        self.value = value

    def __str__(self):
        return str(self.value)

    def set_val(self, new_value):
        """
        Tests the new value is valid and sets the value if it is.

        :param new_value: a new value
        """
        if self.is_valid(new_value):
            self.value = new_value

    def set_val_cast(self, new_value):
        """
        The new value (usually as a string) is casted to the value type through self.parse and it sent to self.set_val.

        :param new_value: a new value
        """
        parsed_value = self.parse(new_value)
        if parsed_value is not None:
            self.set_val(parsed_value)

    def parse(self, new_value_cast):
        """
        Parses a new value string.
        Should be overridden.

        :param new_value_cast: the new value as a string
        :return: the new value as the value's type
        """
        return None

    def is_valid(self, new_value):
        """
        Returns if a new value is valid.
        Should be overridden.

        :param new_value: a new value
        :rtype: bool
        """
        return True


class NumberValue(Value):
    """
    A number value object.

    :var value: the value it holds
    """

    def __init__(self, value, limit='', inclusive='ul', low=0, high=1):
        """
        Number value constructor.
        Limit and inclusive should contain a 'u' for upper and 'l' for lower limit/inclusive comparison.

        :param value: the initial value
        :type limit: str
        :param limit: upper and lower limits
        :type inclusive: str
        :param inclusive: inclusive/non-inclusive comparison
        :type low: float
        :param low: lower limit
        :type low: float
        :param high: upper limit
        """
        super().__init__(value)
        self.limit = limit
        self.inclusive = inclusive
        self.low = low
        self.high = high
        #if not self.is_valid(value):
        #    raise ValueError('Initial value is not valid!')

    def incr(self):
        """
        Increments the value by 1 if valid.
        """
        self.set_val(self.value + 1)

    def decr(self):
        """
        Decrements the value by 1 if valid.
        """
        self.set_val(self.value - 1)

    def is_valid(self, new_value):
        """
        Returns if a new value is valid.

        :param new_value: the new value
        :rtype: bool
        """
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


class IntValue(NumberValue):
    """
    An int value object.

    :var value: the value it holds
    """

    def __str__(self):
        return '%i' % self.value

    def parse(self, new_value_cast):
        try:
            return int(new_value_cast)
        except ValueError:
            return None

    def is_valid(self, new_value):
        if not isinstance(new_value, int):
            raise TypeError('New value must be an int!')
        return super().is_valid(new_value)


class FloatValue(NumberValue):
    """
    A float value object.

    :var value: the value it holds
    """

    def __str__(self):
        return '%.5f' % self.value

    def parse(self, new_value_cast):
        try:
            return float(new_value_cast)
        except ValueError:
            return None

    def is_valid(self, new_value):
        if not isinstance(new_value, float):
            raise TypeError('New value must be a float!')
        super().is_valid(new_value)


class ComplexValue(NumberValue):
    """
    A complex value object. Uses magnitude for comparisons.
    """

    def __str__(self):
        return '%.3f + %.3fj' % (self.value.real, self.value.imag)

    def parse(self, new_value_cast):
        try:
            return complex(new_value_cast)
        except ValueError:
            return None

    def is_valid(self, new_value):
        if not isinstance(new_value, complex):
            raise TypeError('New value must be a complex number!')
        if 'l' in self.limit:
            if 'l' in self.inclusive:
                if abs(new_value) < self.low:
                    return False
            else:
                if abs(new_value) <= self.low:
                    return False
        if 'u' in self.limit:
            if 'u' in self.inclusive:
                if abs(new_value) > self.high:
                    return False
            else:
                if abs(new_value) >= self.high:
                    return False
        return True


class BoolValue(Value):
    """
    A bool value object. Always valid.

    :var value: the value it holds
    """

    def toggle(self):
        """
        Inverts self.value.
        """
        self.value = not self.value

    def parse(self, new_value_cast):
        try:
            return bool(new_value_cast)
        except ValueError:
            return None

    def is_valid(self, new_value):
        if not isinstance(new_value, bool):
            raise TypeError('New value must be a bool!')
        return True


class ValSet:
    """
    A collection of values.
    """

    def __init__(self):
        """
        Value Set constructor.
        """
        self.vals = {}

    def add_int_value(self, name, value, limit='', inclusive='ul', low=0, high=1):
        """
        Adds an int value to the value set.
        Limit and inclusive should contain a 'u' for upper and 'l' for lower limit/inclusive comparison.

        :type name: str
        :param name: the value's name
        :type value: int
        :param value: the initial value
        :type limit: str
        :param limit: upper and lower limits
        :type inclusive: str
        :param inclusive: inclusive/non-inclusive comparison
        :type low: float
        :param low: lower limit
        :type low: float
        :param high: upper limit
        """
        self.vals[name] = IntValue(value, limit, inclusive, low, high)

    def add_float_value(self, name, value, limit='', inclusive='ul', low=0, high=1):
        """
        Adds a float value to the value set.
        Limit and inclusive should contain a 'u' for upper and 'l' for lower limit/inclusive comparison.

        :type name: str
        :param name: the value's name
        :type value: float
        :param value: the initial value
        :type limit: str
        :param limit: upper and lower limits
        :type inclusive: str
        :param inclusive: inclusive/non-inclusive comparison
        :type low: float
        :param low: lower limit
        :type low: float
        :param high: upper limit
        """
        self.vals[name] = FloatValue(value, limit, inclusive, low, high)

    def add_complex_value(self, name, value, limit='', inclusive='ul', low=0, high=1):
        """
        Adds a complex value to the value set.
        Limit and inclusive should contain a 'u' for upper and 'l' for lower limit/inclusive comparison.
        Uses magnitude for comparisons.

        :type name: str
        :param name: the value's name
        :type value: complex
        :param value: the initial value
        :type limit: str
        :param limit: upper and lower limits
        :type inclusive: str
        :param inclusive: inclusive/non-inclusive comparison
        :type low: float
        :param low: lower limit
        :type low: float
        :param high: upper limit
        """
        self.vals[name] = ComplexValue(value, limit, inclusive, low, high)

    def add_bool_value(self, name, value):
        """
        Adds a bool value to the value set.

        :type name: str
        :param name: the value's name
        :type value: bool
        :param value: the initial value
        """
        self.vals[name] = BoolValue(value)

    def get_val(self, name):
        """
        Returns a value from the value set.

        :type name: str
        :param name: the value's name
        :return: the value
        """
        return self.vals[name].value

    def set_val(self, name, value):
        """
        Sets a value to a new value.

        :type name: str
        :param name: the value's name
        :param new_value: a new value
        """
        self.vals[name].set_val(value)

    def get_valobj(self, name):
        """
        Returns a value object from the value set.

        :type name: str
        :param name: the value's name
        :rtype: Value
        :return: the corresponding value object
        """
        return self.vals[name]
