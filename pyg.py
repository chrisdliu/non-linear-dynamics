import pyglet
import pyglet.gl as gl
import pyglet.window as win
import pyglet.graphics as graphics

import time

'''
class Window(win.Window):
    def __init__(self, bg=(0, 0, 0, 1), *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_minimum_size(kwargs['width'], kwargs['height'])
        glClearColor(bg[0], bg[1], bg[2], bg[3])
        self.batch = graphics.Batch()
        self.buttons = []
        self.set_vars()
        self.render()
        self.renderscreen()

    def on_draw(self):
        self.clear()
        glClear(GL_COLOR_BUFFER_BIT)
        self.batch.draw()
        for button in self.buttons:
            button.draw()

    def load_buttons(self):
        for button in self.buttons:
            button.load(self.batch)

    def on_mouse_release(self, x, y, button, modifiers):
        self.mouse_release(x, y, button, modifiers)

    # to be overriden
    def set_vars(self):
        pass

    def render(self):
        pass

    def renderscreen(self):
        pass

    def renderoverlay(self):
        pass

    def mouse_release(self, x, y, button, modifiers):
        print('click: ' + str(x) + ', ' + str(y))
        for button in self.buttons:
            if button.is_inside(x, y):
                button.click()
'''



'''
make button and screen holder dictionaries
make label class and put that in dictionaries as well
'''


'''
ordered groups:
window:
 0: buttons
 1: labels
screen:
-1: background
 0: stuff
'''

'''
ideas:
status line at bottom
'''


class ScreenGroup(graphics.OrderedGroup):
    def __init__(self, x, y, w, h, order, parent=None):
        super().__init__(order, parent=parent)
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def set_state(self):
        """
        Enables a scissor test on the region
        """
        gl.glPushAttrib(gl.GL_ENABLE_BIT | gl.GL_TRANSFORM_BIT | gl.GL_CURRENT_BIT)
        self.was_scissor_enabled = gl.glIsEnabled(gl.GL_SCISSOR_TEST)
        gl.glEnable(gl.GL_SCISSOR_TEST)
        gl.glScissor(int(self.x), int(self.y), int(self.w), int(self.h))

    def unset_state(self):
        """
        Disables the scissor test
        """
        if not self.was_scissor_enabled:
            gl.glDisable(gl.GL_SCISSOR_TEST)
        gl.glPopAttrib()


class Screen:
    def __init__(self, x, y, width, height, bg=(255, 255, 255), valset=None):
        self.x = x
        self.y = y
        self.w = width
        self.h = height
        self.sx = .5
        self.sy = .5
        self.sw = 1
        self.sh = 1

        self.batch = graphics.Batch()
        self.group = ScreenGroup(x, y, width, height, 0)
        self.vertex_lists = {}
        self.vertexes = {}
        self.colors = {}
        self.vertex_types = ('points', 'lines',)
        for type in self.vertex_types:
            self.vertex_lists[type] = None
            self.vertexes[type] = []
            self.colors[type] = []

        self.bg = bg
        self.set_bg(bg)

        self.valset = valset

    def get_val(self, name):
        return self.valset.get_val(name)

    def on_plot(self, px, py):
        return (px - self.sx + self.sw / 2) * self.w / self.sw, (py - self.sy + self.sh / 2) * self.h / self.sh

    def set_bg(self, color):
        if 'bg' not in self.vertex_lists.keys():
            self.vertex_lists['bg'] = None
        if self.vertex_lists['bg']:
            self.vertex_lists['bg'].delete()
        self.vertex_lists['bg'] = self.batch.add(4, gl.GL_QUADS, graphics.OrderedGroup(-1),
            ('v2f', (self.x, self.y, self.x, self.y + self.h, self.x + self.w, self.y + self.h, self.x + self.w, self.y)),
            ('c3B', color * 4))

    def add_point(self, x, y, z=0, color=(0, 0, 0)):
        self.vertexes['points'].extend((x + self.x, y + self.y, z))
        self.colors['points'].extend(color)

    def add_line(self, x1, y1, x2, y2, z=0, color=(0, 0, 0)):
        self.vertexes['lines'].extend((x1 + self.x, y1 + self.y, z, x2 + self.x, y2 + self.y, z))
        self.colors['lines'].extend(color * 2)

    def flush(self):
        for type in self.vertex_types:
            if self.vertex_lists[type]:
                self.vertex_lists[type].delete()
                self.vertex_lists[type] = None
            vlist = None
            if type == 'points':
                vlist = self.batch.add(len(self.vertexes[type]) // 3, gl.GL_POINTS, self.group,
                    ('v3f', self.vertexes[type]), ('c3B', self.colors[type]))
            elif type == 'lines':
                vlist = self.batch.add(len(self.vertexes[type]) // 3, gl.GL_LINES, self.group,
                    ('v3f', self.vertexes[type]), ('c3B', self.colors[type]))
            self.vertex_lists[type] = vlist

        self.clear_buffer()

    def clear_buffer(self):
        for type in self.vertex_types:
            self.vertexes[type] = []
            self.colors[type] = []

    def is_inside(self, x, y):
        return 0 <= x - self.x < self.w and 0 <= y - self.y < self.h

    # to be overriden
    def render(self):
        self.flush()

    def mouse_up(self, x, y, button, modifiers):
        pass

    def on_resize(self, width, height):
        self.group.w = width
        self.group.h = height

    def tick(self):
        pass


class FloatValue:
    def __init__(self, value):
        self.value = value


class IntValue:
    def __init__(self, value):
        self.value = value


class ValSet:
    def __init__(self):
        self.vals = {}

    def add_float(self, name, value):
        self.vals[name] = FloatValue(value)

    def add_int(self, name, value):
        self.vals[name] = IntValue(value)

    def get_obj(self, name):
        return self.vals[name]

    def get_val(self, name):
        return self.vals[name].value


class Field:
    to_string = {
        win.key._0: '0',
        win.key._1: '1',
        win.key._2: '2',
        win.key._3: '3',
        win.key._4: '4',
        win.key._5: '5',
        win.key._6: '6',
        win.key._7: '7',
        win.key._8: '8',
        win.key._9: '9',
        win.key.NUM_0: '0',
        win.key.NUM_1: '1',
        win.key.NUM_2: '2',
        win.key.NUM_3: '3',
        win.key.NUM_4: '4',
        win.key.NUM_5: '5',
        win.key.NUM_6: '6',
        win.key.NUM_7: '7',
        win.key.NUM_8: '8',
        win.key.NUM_9: '9',
        win.key.PERIOD: '.',
        win.key.NUM_DECIMAL: '.',
    }

    def __init__(self, x, y, w, h, name, valfield, batch, limit=False, low=0, high=1, inclusive=True):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.name = name
        self.value = valfield.value
        self.limit = limit
        self.low = low
        self.high = high
        self.inclusive = inclusive
        self.valfield = valfield
        self.input = ''
        self.batch = batch
        self.focus = False
        self.vertex_list = None
        self.label = Label(x, y, self.get_label_text(), batch)

    def get_label_text(self):
        if self.focus:
            return '%s: %s' % (self.name, self.input)
        else:
            return '%s: %s' % (self.name, str(self.value))

    def enter(self):
        print('entered')
        self.focus = True
        self.input = ''
        self.render()

    def exit(self):
        print('exited')
        self.focus = False
        self.parse()
        self.render()

    def parse(self):
        self.input = ''

    def key_press(self, symbol, modifiers):
        if self.focus:
            if symbol == win.key.BACKSPACE:
                if len(self.input) > 0:
                    self.input = self.input[:-1]
            else:
                if symbol in self.to_string.keys():
                    string = self.to_string[symbol]
                    self.input += string
        self.update_label()

    def update_label(self):
        self.label.set_text(self.get_label_text())

    def is_inside(self, x, y):
        return self.x <= x < self.x + self.w and self.y <= y < self.y + self.h

    def render(self):
        self.update_label()
        if self.focus:
            if self.vertex_list:
                self.vertex_list.delete()
            self.vertex_list = self.batch.add(4, gl.GL_QUADS, graphics.OrderedGroup(0),
                ('v2f', (self.x, self.y, self.x + self.w, self.y, self.x + self.w, self.y + self.h, self.x, self.y + self.h)),
                ('c3B', (150, 150, 150) * 4))
        else:
            if self.vertex_list:
                self.vertex_list.delete()
            self.vertex_list = self.batch.add(4, gl.GL_QUADS, graphics.OrderedGroup(0),
                ('v2f', (self.x, self.y, self.x + self.w, self.y, self.x + self.w, self.y + self.h, self.x, self.y + self.h)),
                ('c3B', (100, 100, 100) * 4))


class FloatField(Field):
    def get_label_text(self):
        if self.focus:
            return '%s: %s' % (self.name, self.input)
        else:
            return '%s: %.5f' % (self.name, self.value)

    def parse(self):
        try:
            pvalue = float(self.input)
        except ValueError:
            self.input = ''
            return
        self.input = ''
        if self.limit:
            if self.inclusive:
                if self.low <= pvalue <= self.high:
                    self.value = pvalue
                    self.valfield.value = pvalue
            else:
                if self.low < pvalue < self.high:
                    self.value = pvalue
                    self.valfield.value = pvalue
        else:
            self.value = pvalue
            self.valfield.value = pvalue


class IntField(Field):
    def get_label_text(self):
        if self.focus:
            return '%s: %s' % (self.name, self.input)
        else:
            return '%s: %i' % (self.name, self.value)

    def parse(self):
        try:
            pvalue = int(self.input)
        except ValueError:
            self.input = ''
            return
        self.input = ''
        if self.limit:
            if self.inclusive:
                if self.low <= pvalue <= self.high:
                    self.value = pvalue
                    self.valfield.value = pvalue
            else:
                if self.low < pvalue < self.high:
                    self.value = pvalue
                    self.valfield.value = pvalue
        else:
            self.value = pvalue
            self.valfield.value = pvalue


class Label:
    def __init__(self, x, y, text, batch, color=(255, 255, 255)):
        self.x = x
        self.y = y
        self.text = text
        self.label = pyglet.text.Label(text, font_name='Verdana', font_size=8, x=x, y=y, batch=batch, group=graphics.OrderedGroup(1), color=(color[0], color[1], color[2], 255))

    def set_text(self, text):
        self.label.text = text

    def set_pos(self, x, y):
        self.x = x
        self.y = y
        self.label.x = x
        self.label.y = y


class Button:
    def __init__(self, x, y, w, h, text, batch, action=None):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.text = text
        self.batch = batch
        self.action = action
        self.vertex_list = None
        self.label = Label(x, y, text, batch)

    def mouse_up(self, *args, **kwargs):
        if self.action:
            self.action(*args, **kwargs)

    def is_inside(self, x, y):
        return self.x <= x < self.x + self.w and self.y <= y < self.y + self.h

    def set_text(self, text):
        self.label.set_text(text)

    def render(self):
        if self.vertex_list:
            self.vertex_list.delete()
        self.vertex_list = self.batch.add(4, gl.GL_QUADS, graphics.OrderedGroup(0),
            ('v2f', (self.x, self.y, self.x + self.w, self.y, self.x + self.w, self.y + self.h, self.x, self.y + self.h)),
            ('c3B', (100, 100, 100) * 4))


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

        self.focus = None

        self.set_vars()
        pyglet.clock.schedule_interval(self.tick, 0.1)
        self.render()

    def on_mouse_release(self, x, y, button, modifiers):
        self.mouse_up(x, y, button, modifiers)

    def on_key_press(self, symbol, modifiers):
        self.key_press(symbol, modifiers)

    def add_screen(self, name, screen):
        self.screens[name] = screen

    def add_button(self, name, x, y, w, h, text, action=None):
        self.buttons[name] = Button(x, y, w, h, text, self.batch, action=action)

    def add_label(self, name, x, y, text, color=None):
        if color:
            self.labels[name] = Label(x, y, text, self.batch, color=color)
        else:
            self.labels[name] = Label(x, y, text, self.batch)

    def add_float_field(self, name, x, y, w, h, field_name, valfield, limit=False, low=0, high=1, inclusive=True):
        self.fields[name] = FloatField(x, y, w, h, field_name, valfield, self.batch, limit, low, high, inclusive)

    def add_int_field(self, name, x, y, w, h, field_name, valfield, limit=False, low=0, high=1, inclusive=True):
        self.fields[name] = IntField(x, y, w, h, field_name, valfield, self.batch, limit, low, high, inclusive)

    def on_draw(self):
        self.update_labels()
        self.clear()
        for screen in self.screens.values():
            screen.batch.draw()
        self.batch.draw()

    # render should add points, then flush to the batch
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

    def mouse_up(self, x, y, button, modifiers):
        for screen in self.screens.values():
            if screen.is_inside(x, y):
                screen.mouse_up(x - screen.x, y - screen.y, button, modifiers)
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

    def key_press(self, symbol, modifiers):
        if self.focus:
            self.focus.key_press(symbol, modifiers)
            if symbol == win.key.ENTER:
                self.focus.exit()
                self.focus = None
                self.render()

    def tick(self, dt):
        for screen in self.screens.values():
            screen.tick()

    # to be overriden
    def set_vars(self):
        pass

    def update_labels(self):
        pass
