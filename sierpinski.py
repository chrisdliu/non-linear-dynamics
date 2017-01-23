import pyg
import random
from vmath import *


class SierpScreen(pyg.screen.GraphScreen):
    def render(self):
        tri = (Vec2(self.on_screen(1, 1)), Vec2(self.on_screen(3, 1)), Vec2(self.on_screen2, 1 + 3 ** .5))
        p = Vec2(self.on_screen(2, 1))
        colors = ((255, 0, 0), (0, 255, 0), (0, 0, 255))

        for i in range(self.get_val('iter')):
            r = random.randrange(3)
            p = (p + tri[r]) / 2
            self.add_point(*p, color=colors[r])

        self.flush()

    def resize(self, width, height):
        self.refit(width, height - 200)


class SierpWindow(pyg.window.Window):
    def set_vars(self):
        self.valset.add_int_value('iter', 5000, limit='ul', low=1, high=100000)
        self.valset.add_float_value('zoomratio', .5)

        self.add_screen('main', SierpScreen(0, 200, 500, 500, 2, 2, 4, 4, self.valset, self.get_valobj('zoomratio')))

        self.add_float_field('zoomfield', 100, 130, 120, 15, 'Zoom Ratio', self.get_valobj('zoomratio'))
        self.add_int_field('iterfield', 100, 100, 120, 15, 'Iter', self.get_valobj('iter'))

        self.add_button('resetb', 10, 10, 40, 40, 'Reset', self.get_screen('main').reset_screen)


pyg.run(SierpWindow, caption='Sierpinski')
