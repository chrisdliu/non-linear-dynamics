import pyglet
import pyglet.gl as gl
import pyglet.window as win
import pyglet.graphics as graphics


class Field:
    accepted = {
    }

    def __init__(self, x, y, w, h, name, value, batch):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.name = name
        self.value = value
        self.input = ''
        self.batch = batch
        self.is_focus = False
        self.vertex_list = None
        self.label = Label(x, y, self.get_label_text(), batch)

    def get_label_text(self):
        if self.is_focus:
            return '%s: %s' % (self.name, self.input)
        else:
            return '%s: %s' % (self.name, self.value_str())

    def enter(self):
        print('entered')
        self.is_focus = True
        self.input = ''
        self.render()

    def exit(self):
        print('exited')
        self.is_focus = False
        self.parse()
        self.render()

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

    def is_inside(self, x, y):
        return self.x <= x < self.x + self.w and self.y <= y < self.y + self.h

    def render(self):
        self.update_label()
        if self.is_focus:
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


class Label:
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
