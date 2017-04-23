"""
Defines value objects (Value) and value sets (ValSet) for accessing variables between gui components.
"""
import re


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
        new_value = self.cast(new_value)
        if new_value is not None and self.is_valid(new_value):
            if self.value != new_value:
                self.value = new_value
                return 1
            else:
                self.value = new_value
                return 0

    def cast(self, cast_value):
        return cast_value

    def is_valid(self, new_value):
        """
        Returns if a new value is valid.
        Should be overridden.

        :param new_value: a new value
        :rtype: bool
        """
        return True

    def status(self, inputstr):
        inputcast = self.cast(inputstr)
        if inputcast is not None:
            if self.is_valid(inputcast):
                return True, True
            else:
                return True, False
        else:
            return False, False


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
        if not self.is_valid(value):
            raise ValueError('Initial value is not valid!')

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

    def cast(self, cast_value):
        if isinstance(cast_value, int):
            return cast_value
        else:
            try:
                return int(cast_value)
            except ValueError:
                if isinstance(cast_value, str) and '^' in cast_value:
                    try:
                        a, b = map(int, cast_value.replace(' ', '').split('^'))
                        return a ** b
                    except ValueError:
                        return None
                else:
                    return None


class FloatValue(NumberValue):
    """
    A float value object.

    :var value: the value it holds
    """

    def __str__(self):
        return str(round(self.value, 5))

    def cast(self, cast_value):
        if isinstance(cast_value, float):
            return cast_value
        else:
            try:
                return float(cast_value)
            except ValueError:
                return None


class ComplexValue(NumberValue):
    """
    A complex value object. Uses magnitude for comparisons.

    :var value: the value it holds
    """

    def __str__(self):
        return '%s + %sj' % (str(round(self.value.real, 3)), str(round(self.value.imag, 3)))

    def cast(self, cast_value):
        if isinstance(cast_value, complex):
            return cast_value
        else:
            try:
                return complex(cast_value)
            except ValueError:
                return None

    def is_valid(self, new_value):
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
    A bool value object.

    :var value: the value it holds
    """

    def toggle(self):
        """
        Inverts self.value.
        """
        self.value = not self.value

    def cast(self, cast_value):
        if isinstance(cast_value, bool):
            return cast_value
        else:
            try:
                return bool(cast_value)
            except ValueError:
                return None


class ColorValue(Value):
    def __init__(self, value):
        if isinstance(value, (list, tuple)) and self.is_valid(value):
            self.value = self.cast(value)
        elif isinstance(value, str) and self.is_valid(self.cast(value)):
            self.value = self.cast(value)
        else:
            raise ValueError('Initial value is not valid!')

    def cast(self, cast_value):
        if isinstance(cast_value, (list, tuple)):
            return list(cast_value)
        elif isinstance(cast_value, str):
            if re.match(r'#[0-9,A-F,a-f]{6}', cast_value):
                return list(map(lambda x: int(x, 16), [cast_value[i:i+2] for i in range(1, 7, 2)]))
            else:
                return None

    def is_valid(self, new_value):
        if len(new_value) == 3:
            for c in new_value:
                if not isinstance(c, int) or c < 0 or c > 255:
                    return False
            return True
        else:
            return False

class ValSet:
    """
    A collection of values.
    """

    def __init__(self):
        self.vals = {}

    def add_value(self, name, value):
        self.vals[name] = Value(value)

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

    def add_color_value(self, name, value):
        self.vals[name] = ColorValue(value)

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
