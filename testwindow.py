import pyglet
import pyg


class TestScreen(pyg.screen.Screen):
    def render(self):
        self.add_line(100, 100, 200, 200, color=(255, 0, 0))
        self.add_triangle(300, 100, 400, 100, 350, 200, uniform=False, colors=(255, 0, 0, 0, 255, 0, 0, 0, 255))
        self.add_quad(400, 400, 450, 400, 475, 450, 350, 500, uniform=False, colors=(235, 68, 90, 22, 74, 63, 54, 101, 251, 98, 155, 33))
        self.flush()

    def resize(self, width, height):
        self.w = width
        self.h = height


class TestWindow(pyg.window.Window):
    def set_vars(self):
        self.add_screen('main', (TestScreen(0, 0, 600, 600, bg=(255, 255, 255), valset=None)))


window = TestWindow(width=600, height=600, caption='Logistics Graph', bg=(0, 0, 0, 1), resizable=True)
pyglet.app.run()
