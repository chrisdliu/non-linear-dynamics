"""
Defines the base window.
"""

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

    def __init__(self, width, height, caption='Window Caption', bg=(0, 0, 0), ticktime=0, *args, **kwargs):
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
        self.real_width, self.real_height = width, height

        self.set_bg(bg)

        self._batch = _graphics.Batch()
        self.screens = {}
        self.buttons = {}
        self.labels = {}
        self.fields = {}
        self.sliders = {}
        self.labelrows = {}
        self.boxes = {}
        self.valset = ValSet()

        self.focus = None
        self.hover = None
        self.mousedown = False

        self.set_vars()
        self.update_labels()

        self.ticktime = ticktime
        if ticktime > 0:
            _clock.schedule_interval(self.tick, ticktime)

        if isinstance(self, _win.cocoa.CocoaWindow):
            self.on_resize = self._retina_on_resize

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
                screen.tick(dt)

    # region add gui components
    def add_screen(self, name, screen):
        """
        Adds a screen.

        :type name: str
        :param name: the screen's name
        :type screen: Screen(subclass)
        :param screen: a screen
        """
        self.screens[name] = screen

    def add_box(self, name, box):
        self.boxes[name] = box

    def add_label(self, name, x=0, y=0, text='', color=(255, 255, 255), visible=True, **kwargs):
        """
        Adds a label.

        :type name: str
        :param name: the label's name
        :type x: float
        :param x: x coord
        :type y: float
        :param y: y coord
        :type text: str
        :param text: label text
        :type color: list(int * 3)
        :param color: color
        """
        self.labels[name] = Label(self, name, x, y, text, color, visible, **kwargs)

    def add_button(self, name, x, y, width, height, text, action=None, argsfunc=None, visible=True, interfaced=False):
        """
        Adds a button.

        :type name: str
        :param name: the button's name
        :type x: int
        :param x: x coord
        :type y: int
        :param y: y coord
        :type width: int
        :param width: width
        :type height: int
        :param height: height
        :type text: str
        :param text: button text
        :type action: function
        :param action: function called when pressed
        """
        self.buttons[name] = Button(self, name, x, y, width, height, text, action, argsfunc, visible, interfaced)

    def add_toggle_button(self, name, x, y, width, height, text, boolval, visible=True, interfaced=False):
        """
        Adds a toggle button.

        :type name: str
        :param name: the toggle button's name
        :type x: int
        :param x: x coord
        :type y: int
        :param y: y coord
        :type width: int
        :param width: width
        :type height: int
        :param height: height
        :type text: str
        :param text: button text
        :type boolval: BoolValue
        :param boolval: the bool value linked with the button
        """
        self.buttons[name] = ToggleButton(self, name, x, y, width, height, text, boolval, visible, interfaced)

    def add_int_field(self, name, x, y, w, h, field_name, valobj, visible=True, interfaced=False):
        self.fields[name] = IntField(self, name, x, y, w, h, field_name, valobj, visible, interfaced)

    def add_float_field(self, name, x, y, w, h, field_name, valobj, visible=True, interfaced=False):
        self.fields[name] = FloatField(self, name, x, y, w, h, field_name, valobj, visible, interfaced)

    def add_complex_field(self, name, x, y, w, h, field_name, valobj, visible=True, interfaced=False):
        self.fields[name] = ComplexField(self, name, x, y, w, h, field_name, valobj, visible, interfaced)

    def add_int_hslider(self, name, x, y, w, h, field_name, valobj, low=None, high=None, updatefunc=None, visible=True, interfaced=False):
        self.sliders[name] = IntHSlider(self, name, x, y, w, h, field_name, valobj, low, high, updatefunc, visible, interfaced)

    def add_int_vslider(self, name, x, y, w, h, valobj, low, high, updatefunc=None, visible=True, interfaced=False):
        self.sliders[name] = IntVSlider(self, name, x, y, w, h, valobj, low, high, updatefunc, visible, interfaced)

    def add_label_row(self, name, x, y, w, h, maxchars, maxrows, strfunc, visible=True, interfaced=False):
        self.labelrows[name] = LabelRow(self, name, x, y, w, h, maxchars, maxrows, strfunc, visible, interfaced)
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
    def add_value(self, name, value):
        self.valset.add_value(name, value)

    def add_int_value(self, name, value=0, limit='', inclusive='ul', low=0, high=1):
        """
        Adds an int value to the window's value set.
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
        self.valset.add_int_value(name, value, limit, inclusive, low, high)

    def add_float_value(self, name, value=0, limit='', inclusive='ul', low=0, high=1):
        """
        Adds a float value to the window's value set.
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
        self.valset.add_float_value(name, value, limit, inclusive, low, high)

    def add_complex_value(self, name, value=0, limit='', inclusive='ul', low=0, high=1):
        """
        Adds a complex value to the window's value set.
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
        self.valset.add_complex_value(name, value, limit, inclusive, low, high)

    def add_bool_value(self, name, value):
        """
        Adds a bool value to the window's value set.

        :type name: str
        :param name: the value's name
        :type value: bool
        :param value: the initial value
        """
        self.valset.add_bool_value(name, value)

    def add_color_value(self, name, value='#000000'):
        """
        Adds a color value to the window's value set.

        :type name: str
        :param name: the value's name
        :type value: tuple(int * 3), str
        :param value: the initial value
        """
        self.valset.add_color_value(name, value)

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
        self.clear()

        for screen in self.screens.values():
            if screen.visible:
                screen.draw()

        self.update_labels()

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.width, 0, self.height, -10, 10)
        glMatrixMode(GL_MODELVIEW)
        self._batch.draw()

    def render(self):
        """
        Renders all the gui components and screens.
        Should not be overridden.
        """
        for screen in self.screens.values():
            if screen.visible:
                screen.render()

        # gui components
        for button in self.buttons.values():
            if button.visible and not button.interfaced:
                button.render()
        for field in self.fields.values():
            if field.visible and not field.interfaced:
                field.render()
        for slider in self.sliders.values():
            if slider.visible and not slider.interfaced:
                slider.render()

        for box in self.boxes.values():
            if box.visible and not box.interfaced:
                box.render()

        # gui interfaces
        for labelrow in self.labelrows.values():
            if labelrow.visible:
                labelrow.render()

    # overriding base methods
    def on_draw(self):
        self.draw()

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.real_width, self.real_height = width, height

        for screen in self.screens.values():
            screen.on_resize(width, height)
        self.render()

    def _retina_on_resize(self, width, height):
        """Override default implementation to support retina displays."""
        view = self.context._nscontext.view()
        bounds = view.convertRectToBacking_(view.bounds()).size
        back_width, back_height = (int(bounds.width), int(bounds.height))
        self.real_width, self.real_height = back_width, back_height

        glViewport(0, 0, back_width, back_height)
        glMatrixMode(gl.GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)
        glMatrixMode(gl.GL_MODELVIEW)

        for screen in self.screens.values():
            screen.on_resize(width, height)
        self.render()

    #region events
    def on_mouse_motion(self, x, y, dx, dy):
        self._base_mouse_move(x, y, dx, dy)
        self.mouse_move(x, y, dx, dy)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self._base_mouse_drag(x, y, dx, dy, buttons, modifiers)
        self.mouse_drag(x, y, dx, dy, buttons, modifiers)

    def on_mouse_press(self, x, y, buttons, modifiers):
        if not self.mousedown:
            self.mousedown = True
            self._base_mouse_down(x, y, buttons, modifiers)
            self.mouse_down(x, y, buttons, modifiers)

    def on_mouse_release(self, x, y, buttons, modifiers):
        if self.mousedown:
            self.mousedown = False
            self._base_mouse_up(x, y, buttons, modifiers)
            self.mouse_up(x, y, buttons, modifiers)

    def on_key_press(self, symbol, modifiers):
        self._base_key_down(symbol, modifiers)
        self.key_down(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        self._base_key_up(symbol, modifiers)
        self.key_up(symbol, modifiers)

    def on_text(self, text):
        self.text_input(text)

    def _base_mouse_move(self, x, y, dx, dy):
        for screen in self.screens.values():
            if screen.active:
                screen.mouse_move(x - screen.x, y - screen.y, dx, dy)
        if not self.hover and not self.focus and not self.mousedown:
            for button in self.buttons.values():
                if button.visible and button.is_inside(x, y):
                    self.hover = button
                    button.hover_on()
                    return
            for field in self.fields.values():
                if field.visible and field.is_inside(x, y):
                    self.hover = field
                    field.hover_on()
                    return
            for slider in self.sliders.values():
                if slider.visible and slider.is_inside(x, y):
                    self.hover = slider
                    slider.hover_on()
                    return
        elif self.hover:
            if not self.hover.is_inside(x, y):
                self.hover.hover_off()
                self.hover = None

    def _base_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.hover:
            self.hover.hover_off()
            self.hover = None
        for screen in self.screens.values():
            if screen.active:
                screen.mouse_drag(x - screen.x, y - screen.y, dx, dy, buttons, modifiers)
        if self.focus:
            self.focus.mouse_drag(x - self.focus.x, y - self.focus.y, dx, dy, buttons, modifiers)

    def _base_mouse_down(self, x, y, buttons, modifiers):
        # print('down')
        if self.hover:
            self.hover.hover_off()
            self.hover = None
        for screen in self.screens.values():
            if screen.active and screen.is_inside(x, y):
                screen.mouse_down(x - screen.x, y - screen.y, buttons, modifiers)
                return
        if self.focus:
            # print('down with focus')
            if self.focus.is_inside(x, y):
                self.focus.mouse_down(x - self.focus.x, y - self.focus.y, buttons, modifiers)
            else:
                self.focus.focus_off()
                self.focus = None
        else:
            for button in self.buttons.values():
                if button.visible and button.is_inside(x, y):
                    self.focus = button
                    self.focus.focus_on()
                    return
            for field in self.fields.values():
                if field.visible and field.is_inside(x, y):
                    self.focus = field
                    self.focus.focus_on()
                    return
            for slider in self.sliders.values():
                if slider.visible and slider.is_inside(x, y):
                    self.focus = slider
                    self.focus.focus_on()
                    return

    def _base_mouse_up(self, x, y, buttons, modifiers):
        # print('up')
        if self.hover:
            self.hover.hover_off()
            self.hover = None
        if self.focus:
            # print('up with focus')
            if isinstance(self.focus, (Slider, VSlider)):
                self.focus.focus_off()
                self.focus = None
            elif isinstance(self.focus, Button):
                self.focus.focus_off()
                if self.focus.is_inside(x, y):
                    self.focus.mouse_up(x - self.focus.x, y - self.focus.y, buttons, modifiers)
                self.focus = None
        else:
            for screen in self.screens.values():
                if screen.active and screen.is_inside(x, y):
                    screen.mouse_up(x - screen.x, y - screen.y, buttons, modifiers)
                    return

    def _base_key_down(self, symbol, modifiers):
        if self.focus:
            self.focus.key_down(symbol, modifiers)
            if symbol == _win.key.ENTER:
                self.focus = None
                self.render()
        else:
            for screen in self.screens.values():
                if screen.active:
                    screen.key_down(symbol, modifiers)

    def _base_key_up(self, symbol, modifiers):
        for screen in self.screens.values():
            if screen.active:
                screen.key_up(symbol, modifiers)

    def mouse_move(self, x, y, dx, dy):
        pass

    def mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        pass

    def mouse_down(self, x, y, buttons, modifiers):
        pass

    def mouse_up(self, x, y, buttons, modifiers):
        pass

    def key_down(self, symbol, modifiers):
        pass

    def key_up(self, symbol, modifiers):
        pass

    def text_input(self, text):
        if self.focus:
            self.focus.text_input(text)
    #endregion

    def what(self):
        pass
