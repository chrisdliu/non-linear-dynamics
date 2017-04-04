import pyglet

import pyg


class TestScreen(pyg.screen.Screen2D):
    def render(self):
        pass

    def resize(self, width, height):
        self.w = width
        self.h = height - 200


class TestWindow(pyg.window.Window):
    def set_vars(self):
        self.add_screen('main', (TestScreen(0, 200, 500, 500, self.valset, bg=(255, 255, 255))))

        self.add_button('test', 100, 100, 40, 20, 'Test', lambda: print('asdf'))

        self.add_color_value('color')
        self.add_color_picker('colorpicker', 200, 100, 40, 20, self.get_valobj('color'))


window = TestWindow(width=500, height=700, caption='Logistics Graph', bg=(0, 0, 0, 1), resizable=True)
pyglet.app.run()
