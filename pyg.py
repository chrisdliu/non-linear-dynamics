from pyglet.gl import *


class Button():
    def __init__(self, x, y, w, h, text, action):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.text = text
        self.action = action
        self.label = pyglet.text.Label(text, font_name='Verdana', font_size=8, x=x, y=y)

    def click(self, *args, **kwargs):
        if self.action:
            self.action(*args, **kwargs)

    def is_inside(self, x, y):
        return x >= self.x and x < self.x + self.w and y >= self.y and y < self.y + self.h

    def load(self, batch):
        batch.add(4, GL_QUADS, None, ('v2f', (self.x, self.y, self.x + self.w, self.y, self.x + self.w, self.y + self.h,self.x, self.y + self.h)), ('c3B', (100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100)))

    def draw(self):
        self.label.draw()


class Window(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_minimum_size(600, 800)
        self.batch = pyglet.graphics.Batch()
        self.buttons = []
        self.setvars()
        self.render()
        self.renderscreen()
        self.renderoverlay()

    def on_draw(self):
        print('drawing')
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

    #to be overriden
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