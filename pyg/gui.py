import pyglet
import pyglet.gl as gl
import pyglet.window as win
import pyglet.graphics as graphics


class Field:
    to_string = {
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
        self.focus = False
        self.vertex_list = None
        self.label = Label(x, y, self.get_label_text(), batch)

    def get_label_text(self):
        if self.focus:
            return '%s: %s' % (self.name, self.input)
        else:
            return '%s: %s' % (self.name, self.value_str())

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

    # to be overriden
    def parse(self):
        self.input = ''

    def is_valid(self, pvalue):
        return True

    def value_str(self):
        return str(self.value)


class NumField(Field):
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

    def __init__(self, x, y, w, h, name, value, batch, limit='', inclusive='ul', low=0, high=1):
        super().__init__(x, y, w, h, name, value, batch)
        self.limit = limit
        self.inclusive = inclusive
        self.low = low
        self.high = high

    def is_valid(self, pvalue):
        if 'l' in self.limit:
            print(self.inclusive)
            if 'l' in self.inclusive:
                if self.low > pvalue:
                    return False
            else:
                if self.low >= pvalue:
                    return False
        elif 'u' in self.limit:
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


class Label:
    def __init__(self, x, y, text, batch, color=(255, 255, 255)):
        self.x = x
        self.y = y
        self.text = text
        self.label = pyglet.text.Label(text, font_name='Verdana', font_size=8, x=x, y=y, batch=batch,
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
