import pyglet.clock as clock
from .gui import *
from .valset import *


class Window(window_.Window):
    def __init__(self, width=600, height=600, caption='Window', bg=(0, 0, 0, 1), *args, **kwargs):
        super().__init__(width=width, height=height, caption=caption, *args, **kwargs)
        self.set_minimum_size(width, height)
        gl.glClearColor(*bg)

        self._batch = graphics.Batch()
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
        clock.schedule_interval(self.tick, 0.1)

    def add_screen(self, name, screen):
        self.screens[name] = screen

    def add_button(self, name, x, y, w, h, text, action=None):
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

    def get_val(self, name):
        return self.valset.get_val(name)

    def set_val(self, name, new_value):
        self.valset.set_val(name, new_value)

    def get_valobj(self, name):
        return self.valset.get_valobj(name)

    def draw(self):
        self.update_labels()
        self.clear()
        for screen in self.screens.values():
            if screen.visible:
                screen.draw()
        self._batch.draw()

    def render(self):
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

    def on_resize(self, width, height):
        super().on_resize(width, height)
        for screen in self.screens.values():
            screen.on_resize(width, height)
        self.render()

    # overriding base methods
    def on_draw(self):
        self.draw()

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
                self.focus.exit()
                self.focus = None
        else:
            for button in self.buttons.values():
                if button.is_inside(x, y):
                    self.focus = button
                    self.focus.enter()
                    return
            for field in self.fields.values():
                if field.is_inside(x, y):
                    self.focus = field
                    self.focus.enter()
                    return
            for slider in self.sliders.values():
                if slider.is_inside(x, y):
                    self.focus = slider
                    self.focus.enter()
                    return

    def mouse_up(self, x, y, buttons, modifiers):
        self.mouse = False
        if self.hover:
            self.hover.hover_off()
            self.hover = None
        for screen in self.screens.values():
            if screen.active and screen.is_inside(x, y):
                screen.mouse_up(x - screen.x, y - screen.y, buttons, modifiers)
                return
        if self.focus:
            if isinstance(self.focus, Slider):
                self.focus.exit()
                self.focus = None
                return
            elif isinstance(self.focus, Button):
                self.focus.exit()
                if self.focus.is_inside(x, y) and self.focus.active:
                    self.focus.mouse_up()
                self.focus = None
                return

        #print('click: ' + str(x) + ', ' + str(y))

    def key_down(self, symbol, modifiers):
        if self.focus:
            self.focus.key_down(symbol, modifiers)
            if symbol == window_.key.ENTER:
                self.focus = None
                self.render()
        else:
            for screen in self.screens.values():
                if screen.active:
                    screen.key_down(symbol, modifiers)

    def key_up(self, symbol, modifiers):
        for screen in self.screens.values():
            if screen.active:
                screen.key_up(symbol, modifiers)

    def text_input(self, text):
        if self.focus:
            self.focus.text_input(text)

    def tick(self, dt):
        for screen in self.screens.values():
            if screen.active:
                screen.tick()

    # to be overriden
    def set_vars(self):
        pass

    def update_labels(self):
        pass
