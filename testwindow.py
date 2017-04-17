import pyg
import pyglet
import numpy as np


class TestScreen(pyg.screen.GraphScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.pixels = np.full(100 * 100 * 3, 127, dtype=np.ubyte)
        #raw = np.ctypeslib.as_ctypes(self.pixels)
        #self.img = pyglet.image.ImageData(100, 100, 'RGB', raw)

        #self.pixels2 = np.array([255, 0, 0] * 10 * 3, dtype=np.ubyte)
        #raw = np.ctypeslib.as_ctypes(self.pixels2)
        #self.img2 = pyglet.image.ImageData(10, 1, 'RGB', raw)

    def render(self):
        #self.add_triangle(0, 0, 100, 0, 0, 100, color=(50, 50, 200))
        #self.flush()
        pass

    def resize(self, width, height):
        self.set_size(width - 200, height)

    def draw(self):
        super().draw()
        #self.img._current_texture = None
        #self.img.blit(100, 100)
        #self.pixels[1] = 0
        #self.img.get_data('RGB', 300)
        #self.img._current_data[:3] = [0, 255, 0]

        #self.img._current_data_buf[:3] = [0, 255, 0]
        #self.img2.blit(100, 200)


class TestWindow(pyg.window.Window):
    def set_vars(self):
        self.add_float_value('gz', .5)
        self.add_screen('main', TestScreen(self, 200, 0, 500, 500, 50, 50, 50, 50, 'gz'))
        #self.add_screen('main', TestScreen(self, 200, 0, 500, 500))

pyglet.clock.schedule_interval(lambda dt: print(dt), .01)
pyg.run(TestWindow, width=700, height=500)
