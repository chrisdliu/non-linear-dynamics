import pyglet.clock as _clock
import pyglet.graphics as _graphics
import pyglet.window as _win

from pyglet.gl import *

from math import floor as _floor

from .gui import *
from .valset import *


class Window(_win.Window):
    """
    Base window class. Holds all parts of the gui and all the screens.

    :var width: width
    :var height: height
    :var bg: background color
    :var screens: dictionary of screens
    :var buttons: dictionary of buttons
    :var labels: dictionary of labels
    :var fields: dictionary of fields
    :var sliders: dictionary of sliders
    :var valset: the window's valset
    """

    def __init__(self, width=600, height=600, caption='Window Caption', bg=(0, 0, 0), ticktime=0, *args, **kwargs):
        """
        Window constructor.

        :type width: int
        :param width: width
        :type height: int
        :param height: height
        :type caption: str
        :param caption: caption
        :type bg: list(int * 3)
        :param bg: background color
        :type ticktime: float
        :param ticktime: interval between ticks in seconds, zero to disable ticking
        """
        super().__init__(width=width, height=height, caption=caption, *args, **kwargs)
        self.set_minimum_size(width, height)

        glClearColor(*[_floor(color % 256) / 255 for color in bg], 1)
        self.bg = bg

        self._batch = _graphics.Batch()
        self.screens = {}
        self.buttons = {}
        self.labels = {}
        self.fields = {}
        self.sliders = {}
        self.valset = ValSet()

        self.focus = None
        self.hover = None
        self.mouse = False

        self.set_vars()
        self.update_labels()

        self.ticktime = ticktime
        if ticktime > 0:
            _clock.schedule_interval(self.tick, ticktime)

    def set_vars(self):
        """
        Called by the constructor.
        All gui and value set objects should be added here.
        Should be overridden.
        """
        pass

    def update_labels(self):
        """
        Called before every draw.
        Labels and other gui components should be updated here.
        Should be overridden.
        """
        pass

    def set_bg(self, bg):
        """
        Sets the background color.

        :type bg: list(int * 3)
        :param bg: background color
        """
        glClearColor(*[_floor(color % 256) / 255 for color in bg], 1)
        self.bg = bg

    def tick(self, dt):
        for screen in self.screens.values():
            if screen.active:
                screen.tick()

    # region add gui components
    def add_screen(self, name, screen):
        """
        Adds a screen.

        :type name: str
        :param name: name
        :type screen: Screen(subclass)
        :param screen: a screen
        """
        self.screens[name] = screen

    def add_button(self, name, x, y, w, h, text, action=None):
        """
        Adds a button.

        :param name:
        :param x:
        :param y:
        :param w:
        :param h:
        :param text:
        :param action:
        :return:
        """
        self.buttons[name] = Button(x, y, w, h, text, self._batch, action=action)

    def add_toggle_button(self, name, x, y, w, h, text, boolval):
        self.buttons[name] = ToggleButton(x, y, w, h, text, boolval, self._batch)

    def add_label(self, name, x, y, text='', color=(255, 255, 255)):
        self.labels[name] = Label(x, y, text, self._batch, color=color)

    def add_int_field(self, name, x, y, w, h, field_name, valobj):
        self.fields[name] = IntField(x, y, w, h, field_name, valobj, self._batch)

    def add_float_field(self, name, x, y, w, h, field_name, valobj):
        self.fields[name] = FloatField(x, y, w, h, field_name, valobj, self._batch)

    def add_complex_field(self, name, x, y, w, h, field_name, valobj):
        self.fields[name] = ComplexField(x, y, w, h, field_name, valobj, self._batch)

    def add_int_slider(self, name, x, y, w, h, offs, field_name, valobj, low, high):
        self.sliders[name] = IntSlider(x, y, w, h, offs, field_name, valobj, low, high, self._batch)
    # endregion

    # region get gui components
    def get_screen(self, name):
        return self.screens[name]

    def get_button(self, name):
        return self.buttons[name]

    def get_label(self, name):
        return self.labels[name]

    def get_field(self, name):
        return self.fields[name]

    def get_slider(self, name):
        return self.sliders[name]
    # endregion

    # region valset functions
    def add_int_value(self, name, value, limit='', inclusive='ul', low=0, high=1):
        self.valset.add_int_value(name, value, limit, inclusive, low, high)

    def add_float_value(self, name, value, limit='', inclusive='ul', low=0, high=1):
        self.valset.add_float_value(name, value, limit, inclusive, low, high)

    def add_complex_value(self, name, value, limit='', inclusive='ul', low=0, high=1):
        self.valset.add_complex_value(name, value, limit, inclusive, low, high)

    def add_bool_value(self, name, value):
        self.valset.add_bool_value(name, value)

    def get_val(self, name):
        """
        Returns a value from the value set.

        :type name: str
        :param name: the value's name
        :return: the value
        """
        return self.valset.get_val(name)

    def set_val(self, name, new_value):
        """
        Sets a value to a new value.

        :type name: str
        :param name: the value's name
        :param new_value: a new value
        """
        self.valset.set_val(name, new_value)

    def get_valobj(self, name):
        """
        Returns a value object from the value set.

        :type name: str
        :param name: the value's name
        :rtype: Value
        :return: the corresponding value object
        """
        return self.valset.get_valobj(name)
    # endregion

    def draw(self):
        """
        Called by on_draw().
        Draws all the batches to the screen.
        Should not be overridden.
        """
        self.update_labels()
        self.clear()
        for screen in self.screens.values():
            if screen.visible:
                screen.draw()

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.width, 0, self.height, -10, 10)
        glMatrixMode(GL_MODELVIEW)
        #glEnable(GL_DEPTH_TEST)
        self._batch.draw()
        #glDisable(GL_DEPTH_TEST)

    def render(self):
        """
        Renders all the gui components and screens.
        Should not be overridden.
        """
        for screen in self.screens.values():
            if screen.visible:
                screen.render()
        for button in self.buttons.values():
            if button.visible:
                button.render()
        for field in self.fields.values():
            field.render()
        for slider in self.sliders.values():
            slider.render()

    # overriding base methods
    def on_draw(self):
        self.draw()

    def on_resize(self, width, height):
        super().on_resize(width, height)
        for screen in self.screens.values():
            screen.on_resize(width, height)
        self.render()

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_move(x, y, dx, dy)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.mouse_drag(x, y, dx, dy, buttons, modifiers)

    def on_mouse_press(self, x, y, buttons, modifiers):
        self.mouse_down(x, y, buttons, modifiers)

    def on_mouse_release(self, x, y, buttons, modifiers):
        self.mouse_up(x, y, buttons, modifiers)

    def on_key_press(self, symbol, modifiers):
        self.key_down(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        self.key_up(symbol, modifiers)

    def on_text(self, text):
        self.text_input(text)

    # for subclasses
    def mouse_move(self, x, y, dx, dy):
        """
        Called when the mouse moves.
        Should be called if overridden.
        Refer to pyglet for documentation.
        """
        for screen in self.screens.values():
            if screen.active:
                screen.mouse_move(x - screen.x, y - screen.y, dx, dy)
                break
        if not self.hover and not self.focus and not self.mouse:
            for button in self.buttons.values():
                if button.is_inside(x, y):
                    self.hover = button
                    button.hover_on()
                    return
            for field in self.fields.values():
                if field.is_inside(x, y):
                    self.hover = field
                    field.hover_on()
                    return
            for slider in self.sliders.values():
                if slider.is_inside(x, y):
                    self.hover = slider
                    slider.hover_on()
                    return
        elif self.hover:
            if not self.hover.is_inside(x, y):
                self.hover.hover_off()
                self.hover = None

    def mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        """
        Called when the mouse is dragged.
        Should be called if overridden.
        Refer to pyglet for documentation.
        """
        if self.hover:
            self.hover.hover_off()
            self.hover = None
        for screen in self.screens.values():
            if screen.active:
                screen.mouse_drag(x - screen.x, y - screen.y, dx, dy, buttons, modifiers)
        if self.focus:
            self.focus.mouse_drag(x - self.focus.x, y - self.focus.y, dx, dy, buttons, modifiers)
            if isinstance(self.focus, Slider):
                self.render()

    def mouse_down(self, x, y, buttons, modifiers):
        """
        Called when the a mouse button is pressed.
        Should be called if overridden.
        Refer to pyglet for documentation.
        """
        self.mouse = True
        if self.hover:
            self.hover.hover_off()
            self.hover = None
        for screen in self.screens.values():
            if screen.active and screen.is_inside(x, y):
                screen.mouse_down(x - screen.x, y - screen.y, buttons, modifiers)
                return
        if self.focus:
            if self.focus.is_inside(x, y):
                self.focus.mouse_down(x, y, buttons, modifiers)
            else:
                self.focus.focus_off()
                self.focus = None
        else:
            for button in self.buttons.values():
                if button.is_inside(x, y):
                    self.focus = button
                    self.focus.focus_on()
                    return
            for field in self.fields.values():
                if field.is_inside(x, y):
                    self.focus = field
                    self.focus.focus_on()
                    return
            for slider in self.sliders.values():
                if slider.is_inside(x, y):
                    self.focus = slider
                    self.focus.focus_on()
                    return

    def mouse_up(self, x, y, buttons, modifiers):
        """
        Called when a mouse button is released.
        Should be called if overridden.
        Refer to pyglet for documentation.
        """
        self.mouse = False
        if self.hover:
            self.hover.hover_off()
            self.hover = None
        if self.focus:
            if isinstance(self.focus, Slider):
                self.focus.focus_off()
                self.focus = None
            elif isinstance(self.focus, Button):
                self.focus.focus_off()
                if self.focus.is_inside(x, y):  # and self.focus.active:
                    self.focus.mouse_up()
                self.focus = None
            return
        for screen in self.screens.values():
            if screen.active and screen.is_inside(x, y):
                screen.mouse_up(x - screen.x, y - screen.y, buttons, modifiers)
                return

    def key_down(self, symbol, modifiers):
        """
        Called when a key is pressed.
        Should be called if overridden.
        Refer to pyglet for documentation.
        """
        if self.focus:
            self.focus.key_down(symbol, modifiers)
            if symbol == _win.key.ENTER:
                self.focus = None
                self.render()
        else:
            for screen in self.screens.values():
                if screen.active:
                    screen.key_down(symbol, modifiers)

    def key_up(self, symbol, modifiers):
        """
        Called when a key is released.
        Should be called if overridden.
        Refer to pyglet for documentation.
        """
        for screen in self.screens.values():
            if screen.active:
                screen.key_up(symbol, modifiers)

    def text_input(self, text):
        """
        Called when text is entered.
        Should be called if overridden.
        Refer to pyglet for documentation.
        """
        if self.focus:
            self.focus.text_input(text)
