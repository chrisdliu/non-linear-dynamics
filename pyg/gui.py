import pyglet
import pyglet.gl as gl
import pyglet.window as win
import pyglet.graphics as graphics


class GUI_Obj:
    def __init__(self, x, y, w, h, focusable=False):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.focusable = focusable
        self.is_focus = False
        self.vertex_lists = []

    def is_inside(self, x, y):
        return self.x <= x < self.x + self.w and self.y <= y < self.y + self.h

    def clear_vlists(self):
        for vlist in self.vertex_lists:
            vlist.delete()
            self.vertex_lists.remove(vlist)

    def add_vlist(self, vlist):
        self.vertex_lists.append(vlist)

    def enter(self):
        if self.focusable:
            self.is_focus = True
            self.render()

    def exit(self):
        self.is_focus = False
        self.render()

    def render(self):
        pass

    def key_down(self, symbol, modifiers):
        pass

    def text_input(self, text):
        pass

    def mouse_down(self, x, y, buttons, modifiers):
        pass

    def mouse_up(self, x, y, buttons, modifiers):
        pass

    def mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        pass


class Field(GUI_Obj):
    accepted = []

    def __init__(self, x, y, w, h, name, value, batch):
        super().__init__(x, y, w, h, True)
        self.name = name
        self.value = value
        self.input = ''
        self.batch = batch
        self.label = Label(x, y, self.get_label_text(), batch)

    def get_label_text(self):
        if self.is_focus:
            return '%s: %s' % (self.name, self.input)
        else:
            return '%s: %s' % (self.name, self.value_str())

    def enter(self):
        self.input = ''
        super().enter()

    def exit(self):
        self.parse()
        super().exit()

    def key_down(self, symbol, modifiers):
        if symbol == win.key.ENTER:
            self.exit()
        elif symbol == win.key.BACKSPACE:
            if len(self.input) > 0:
                self.input = self.input[:-1]
        self.update_label()
    
    def text_input(self, text):
        if text in self.accepted:
            self.input += text
        self.update_label()

    def update_label(self):
        self.label.set_text(self.get_label_text())

    def render(self):
        self.update_label()
        if self.is_focus:
            self.add_vlist(self.batch.add(4, gl.GL_QUADS, graphics.OrderedGroup(0),
                ('v2f', (self.x, self.y, self.x + self.w, self.y, self.x + self.w, self.y + self.h, self.x, self.y + self.h)),
                ('c3B', (150, 150, 150) * 4)))
        else:
            self.add_vlist(self.batch.add(4, gl.GL_QUADS, graphics.OrderedGroup(0),
                ('v2f', (self.x, self.y, self.x + self.w, self.y, self.x + self.w, self.y + self.h, self.x, self.y + self.h)),
                ('c3B', (100, 100, 100) * 4)))

    # to be overriden
    def parse(self):
        self.input = ''

    def is_valid(self, pvalue):
        return True

    def value_str(self):
        return str(self.value)


class NumField(Field):
    accepted = [
        '0',
        '1',
        '2',
        '3',
        '4',
        '5',
        '6',
        '7',
        '8',
        '9',
        '.',
        '+',
        '-',
        'j',
    ]

    def __init__(self, x, y, w, h, name, value, batch, limit='', inclusive='ul', low=0, high=1):
        super().__init__(x, y, w, h, name, value, batch)
        self.limit = limit
        self.inclusive = inclusive
        self.low = low
        self.high = high

    def is_valid(self, pvalue):
        if 'l' in self.limit:
            if 'l' in self.inclusive:
                if self.low > pvalue:
                    return False
            else:
                if self.low >= pvalue:
                    return False
        if 'u' in self.limit:
            if 'u' in self.inclusive:
                if pvalue > self.high:
                    return False
            else:
                if pvalue >= self.high:
                    return False
        return True


class FloatField(NumField):
    def value_str(self):
        return '%.5f' % self.value.value

    def parse(self):
        try:
            pvalue = float(self.input)
        except ValueError:
            self.input = ''
            return
        self.input = ''
        if self.is_valid(pvalue):
            self.value.value = pvalue


class IntField(NumField):
    def value_str(self):
        return '%i' % self.value.value

    def parse(self):
        try:
            pvalue = int(self.input)
        except ValueError:
            self.input = ''
            return
        self.input = ''
        if self.is_valid(pvalue):
            self.value.value = pvalue


class ComplexField(NumField):
    def value_str(self):
        return '%.3f + %.3fj' % (self.value.value.real, self.value.value.imag)

    def parse(self):
        try:
            pvalue = complex(self.input)
        except ValueError:
            self.input = ''
            return
        self.input = ''
        if self.is_valid(pvalue):
            self.value.value = pvalue


class Label(GUI_Obj):
    def __init__(self, x, y, text, batch, color=(255, 255, 255)):
        self.x = x
        self.y = y
        self.text = text
        self.label = pyglet.text.Label(text, font_name='Menlo', font_size=8, x=x, y=y, batch=batch,
            group=graphics.OrderedGroup(1), color=(color[0], color[1], color[2], 255))

    def set_text(self, text):
        self.label.text = text

    def set_pos(self, x, y):
        self.x = x
        self.y = y
        self.label.x = x
        self.label.y = y


class Button(GUI_Obj):
    def __init__(self, x, y, w, h, text, batch, action=None):
        super().__init__(x, y, w, h)
        self.batch = batch
        self.action = action
        self.label = Label(x, y, text, batch)

    def mouse_up(self, *args, **kwargs):
        if self.action:
            self.action(*args, **kwargs)

    def set_text(self, text):
        self.label.set_text(text)

    def render(self):
        self.clear_vlists()
        self.add_vlist(self.batch.add(4, gl.GL_QUADS, graphics.OrderedGroup(0),
              ('v2f', (self.x, self.y, self.x + self.w, self.y, self.x + self.w, self.y + self.h, self.x, self.y + self.h)),
              ('c3B', (100, 100, 100) * 4)))


class ToggleButton(Button):
    def __init__(self, x, y, w, h, text, boolval, batch):
        self.boolval = boolval
        super().__init__(x, y, w, h, text, batch, action=self.toggle)

    def toggle(self):
        self.boolval.toggle()
        self.render()

    def render(self):
        self.clear_vlists()
        if self.boolval.value:
            self.add_vlist(self.batch.add(4, gl.GL_QUADS, graphics.OrderedGroup(0),
                  ('v2f', (self.x, self.y, self.x + self.w, self.y, self.x + self.w, self.y + self.h, self.x, self.y + self.h)),
                  ('c3B', (150, 150, 150) * 4)))
        else:
            self.add_vlist(self.batch.add(4, gl.GL_QUADS, graphics.OrderedGroup(0),
                  ('v2f', (self.x, self.y, self.x + self.w, self.y, self.x + self.w, self.y + self.h, self.x, self.y + self.h)),
                  ('c3B', (100, 100, 100) * 4)))


class Slider(GUI_Obj):
    def __init__(self, x, y, w, h, offs, field_name, valobj, low, high, batch):
        super().__init__(x, y, w, h, True)
        self.offs = offs
        self.field_name = field_name
        self.valobj = valobj
        self.low = low
        self.high = high
        self.slider_pos = (valobj.value - low) / (high - low)
        self.batch = batch
        self.label = Label(x, y, self.get_label_text(), batch)
        self.updated = False

    def is_updated(self):
        if self.updated:
            self.updated = False
            return True
        return False

    def get_label_text(self):
        return self.field_name + ': ' + str(self.valobj.value)

    def is_inside(self, x, y):
        return self.x <= x < self.x + self.w + self.offs and self.y <= y < self.y + self.h

    def render(self):
        self.clear_vlists()
        if self.is_focus:
            self.add_vlist(self.batch.add(4, gl.GL_QUADS, graphics.OrderedGroup(0),
                ('v2f', (self.x, self.y, self.x + self.w + self.offs, self.y, self.x + self.w + self.offs, self.y + self.h, self.x, self.y + self.h)),
                ('c3B', (150, 150, 150) * 4)))
        else:
            self.add_vlist(self.batch.add(4, gl.GL_QUADS, graphics.OrderedGroup(0),
                ('v2f', (self.x, self.y, self.x + self.w + self.offs, self.y, self.x + self.w + self.offs, self.y + self.h, self.x, self.y + self.h)),
                ('c3B', (100, 100, 100) * 4)))
        self.add_vlist(self.batch.add(4, gl.GL_QUADS, graphics.OrderedGroup(1),
            ('v2f', (self.x + self.slider_pos * self.w + self.offs, self.y, self.x + self.slider_pos * self.w + 2 + self.offs, self.y,
                     self.x + self.slider_pos * self.w + 2 + self.offs, self.y + self.h, self.x + self.slider_pos * self.w + self.offs, self.y + self.h)),
            ('c3B', (240, 0, 240) * 4)))

    def mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.slider_pos = (x - self.offs) / self.w
        if self.slider_pos < 0:
            self.slider_pos = 0
        if self.slider_pos > 1:
            self.slider_pos = 1
        new_value = (self.slider_pos * (self.high - self.low)) + self.low
        self.valobj.value = self.parse(new_value)
        self.label.set_text(self.get_label_text())
        self.render()

    def parse(self, new_value):
        self.updated = True
        return new_value


class IntSlider(Slider):
    def parse(self, new_value):
        new_value = int(new_value)
        if self.valobj.value != new_value:
            self.updated = True
        return new_value

