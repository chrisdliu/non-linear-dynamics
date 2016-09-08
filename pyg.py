from pyglet.gl import *


class Window(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_minimum_size(600, 800)
        self.batch = pyglet.graphics.Batch()

        self.setvars()
        self.load()

    def on_draw(self):
        self.clear()
        glClear(GL_COLOR_BUFFER_BIT)
        self.batch.draw()

    #to be overriden
    def setvars(self):
        pass

    def load(self):
        pass