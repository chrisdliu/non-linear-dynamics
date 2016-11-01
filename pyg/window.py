import pyglet.clock as clock
from .gui import *
from .valset import *


class Window(win.Window):
    def __init__(self, width=600, height=600, caption='Window', bg=(0, 0, 0, 1), *args, **kwargs):
        super().__init__(width=width, height=height, caption=caption, *args, **kwargs)
        self.set_minimum_size(width, height)
        gl.glClearColor(bg[0], bg[1], bg[2], bg[3])

        # batch for the window
        # no vertex_list for window
        self.batch = graphics.Batch()
        self.screens = {}
        self.buttons = {}
        self.labels = {}
        self.fields = {}
        self.valset = ValSet()

        self.focus = None

        self.set_vars()
        self.update_labels()
        clock.schedule_interval(self.tick, 0.1)
        self.render()

    def add_screen(self, name, screen):
        self.screens[name] = screen

    def add_button(self, name, x, y, w, h, text, action=None):
        self.buttons[name] = Button(x, y, w, h, text, self.batch, action=action)

    def add_label(self, name, x, y, text, color=None):
        if color:
            self.labels[name] = Label(x, y, text, self.batch, color=color)
        else:
            self.labels[name] = Label(x, y, text, self.batch)

    def add_float_field(self, name, x, y, w, h, field_name, value, limit='', inclusive='ul', low=0, high=1):
        self.fields[name] = FloatField(x, y, w, h, field_name, value, self.batch, limit, inclusive, low, high)

    def add_int_field(self, name, x, y, w, h, field_name, value, limit='', inclusive='ul', low=0, high=1):
        self.fields[name] = IntField(x, y, w, h, field_name, value, self.batch, limit, inclusive, low, high)

    def add_complex_field(self, name, x, y, w, h, field_name, value, limit='', inclusive='ul', low=0, high=1):
        self.fields[name] = ComplexField(x, y, w, h, field_name, value, self.batch, limit, inclusive, low, high)

    def on_draw(self):
        self.update_labels()
        self.clear()
        for screen in self.screens.values():
            screen.on_draw()
        self.batch.draw()

    def render(self):
        for screen in self.screens.values():
            screen.render()
        for button in self.buttons.values():
            button.render()
        for field in self.fields.values():
            field.render()

    def on_resize(self, width, height):
        super().on_resize(width, height)
        for screen in self.screens.values():
            screen.on_resize(width, height)
        self.render()

    # overriding base methods
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

    # for subclasses
    def mouse_move(self, x, y, dx, dy):
        for screen in self.screens.values():
            screen.mouse_move(x - screen.x, y - screen.y, dx, dy)

    def mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        for screen in self.screens.values():
            screen.mouse_drag(x - screen.x, y - screen.y, dx, dy, buttons, modifiers)

    def mouse_down(self, x, y, buttons, modifiers):
        for screen in self.screens.values():
            if screen.is_inside(x, y):
                screen.mouse_down(x - screen.x, y - screen.y, buttons, modifiers)

    def mouse_up(self, x, y, buttons, modifiers):
        for screen in self.screens.values():
            if screen.is_inside(x, y):
                screen.mouse_up(x - screen.x, y - screen.y, buttons, modifiers)
                break
        for b in self.buttons.values():
            if b.is_inside(x, y):
                b.mouse_up()
                break
        in_field = False
        for f in self.fields.values():
            if f.is_inside(x, y):
                if self.focus:
                    if f != self.focus:
                        self.focus.exit()
                    else:
                        in_field = True
                        break
                self.focus = f
                self.focus.enter()
                in_field = True
                break
        if not in_field:
            if self.focus:
                self.focus.exit()
            self.focus = None

        print('click: ' + str(x) + ', ' + str(y))

    def key_down(self, symbol, modifiers):
        for screen in self.screens.values():
            screen.key_down(symbol, modifiers)
        if self.focus:
            self.focus.key_press(symbol, modifiers)
            if symbol == win.key.ENTER:
                self.focus.exit()
                self.focus = None
                self.render()

    def key_up(self, symbol, modifiers):
        for screen in self.screens.values():
            screen.key_up(symbol, modifiers)

    def tick(self, dt):
        for screen in self.screens.values():
            screen.tick()

    # to be overriden
    def set_vars(self):
        pass

    def update_labels(self):
        pass
