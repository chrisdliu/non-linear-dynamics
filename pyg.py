from pyglet.gl import *


class Window(pyglet.window.Window):
    def __init__(self, bg=(0, 0, 0, 1), *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_minimum_size(kwargs['width'], kwargs['height'])
        glClearColor(bg[0], bg[1], bg[2], bg[3])
        self.batch = pyglet.graphics.Batch()
        self.buttons = []
        self.setvars()
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
    def setvars(self):
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


class Button:
    def __init__(self, x, y, w, h, text, action=None):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.text = text
        self.action = action
        self.vertex_list = None
        self.label = pyglet.text.Label(text, font_name='Verdana', font_size=8, x=x, y=y)

    def mouse_up(self, *args, **kwargs):
        if self.action:
            self.action(*args, **kwargs)

    def is_inside(self, x, y):
        return self.x <= x < self.x + self.w and self.y <= y < self.y + self.h

    def render(self, batch):
        if self.vertex_list:
            self.vertex_list.delete()
        self.vertex_list = batch.add(4, GL_QUADS, pyglet.graphics.OrderedGroup(2),
            ('v2f', (self.x, self.y, self.x + self.w, self.y, self.x + self.w, self.y + self.h, self.x, self.y + self.h)),
            ('c3B', (100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100)))

    def draw_label(self):
        self.label.draw()

'''
make button and screen holder dictionaries
make label class and put that in dictionaries as well
'''

class Screen:
    def __init__(self, x, y, width, height, bg=(255, 255, 255)):
        self.x = x
        self.y = y
        self.w = width
        self.h = height
        self.sx = .5
        self.sy = .5
        self.sw = 1
        self.sh = 1
        self.mousedown = False

        self.batch = pyglet.graphics.Batch()
        self.vertex_lists = {}
        self.vertexes = {}
        self.colors = {}
        self.vertex_types = ('points', 'lines',)
        for type in self.vertex_types:
            self.vertex_lists[type] = None
            self.vertexes[type] = []
            self.colors[type] = []

        self.bg = bg
        self.setbg(bg)
        self.setvars()

    def onplot(self, px, py):
        return ((px - self.sx + self.sw / 2) * self.w / self.sw, (py - self.sy + self.sh / 2) * self.h / self.sh)

    def setbg(self, color):
        if 'bg' not in self.vertex_lists.keys():
            self.vertex_lists['bg'] = None
        if self.vertex_lists['bg']:
            self.vertex_lists['bg'].delete()
        self.vertex_lists['bg'] = self.batch.add(4, GL_QUADS, pyglet.graphics.OrderedGroup(0),
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
                vlist = self.batch.add(len(self.vertexes[type]) // 3, GL_POINTS, pyglet.graphics.OrderedGroup(1),
                    ('v3f', self.vertexes[type]), ('c3B', self.colors[type]))
            elif type == 'lines':
                vlist = self.batch.add(len(self.vertexes[type]) // 3, GL_LINES, pyglet.graphics.OrderedGroup(1),
                    ('v3f', self.vertexes[type]), ('c3B', self.colors[type]))
            self.vertex_lists[type] = vlist

        self.clearbuffer()

    def clearbuffer(self):
        for type in self.vertex_types:
            self.vertexes[type] = []
            self.colors[type] = []

    def is_inside(self, x, y):
        return 0 <= x - self.x < self.w and 0 <= y - self.y < self.h

    # to be overriden
    def setvars(self):
        pass

    def render(self):
        pass

    def on_resize(self, width, height):
        pass

    def tick(self):
        pass


class Window2(pyglet.window.Window):
    def __init__(self, width=600, height=600, caption='Window', bg=(0, 0, 0, 1), *args, **kwargs):
        super().__init__(width=width, height=height, caption=caption, *args, **kwargs)
        self.set_minimum_size(width, height)
        glClearColor(bg[0], bg[1], bg[2], bg[3])
        self.mousedown = False

        # batch for the window
        # no vertex_list for window
        self.batch = pyglet.graphics.Batch()
        self.screens = []
        self.buttons = []
        self.labels = []

        self.setvars()
        pyglet.clock.schedule_interval(self.tick, 0.1)
        self.render()

    def on_mouse_release(self, x, y, button, modifiers):
        self.mouse_up(x, y, button, modifiers)

    def on_draw(self):
        print('drawing')
        self.redraw_labels()
        self.clear()
        self.batch.draw()
        for screen in self.screens:
            screen.batch.draw()
        for button in self.buttons:
            button.draw_label()
        for label in self.labels:
            label.draw()

    # render should add points, then flush to the batch
    def render(self):
        for screen in self.screens:
            screen.render()
        for button in self.buttons:
            button.render(self.batch)

    def on_resize(self, width, height):
        super().on_resize(width, height)
        for screen in self.screens:
            screen.on_resize(width, height)
        self.render()

    # to be overriden
    def setvars(self):
        pass

    def mouse_up(self, x, y, button, modifiers):
        for screen in self.screens:
            if screen.is_inside(x, y):
                screen.mouse_up(x - screen.x, y - screen.y, button, modifiers)
        for b in self.buttons:
            if b.is_inside(x, y):
                b.mouse_up()
        print('click: ' + str(x) + ', ' + str(y))

    def redraw_labels(self):
        pass

    def tick(self, dt):
        for screen in self.screens:
            screen.tick()
