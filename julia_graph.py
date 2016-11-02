import pyg
import pyglet
import time


class JuliaScreen(pyg.screen.GraphScreen):
    def reset(self):
        self.sx = 0
        self.sy = 0
        self.sw = 5
        self.sh = 5
        self.render()

    def render(self):
        lx1, ly1 = self.on_screen(0, -10)
        lx2, ly2 = self.on_screen(0, 10)
        self.add_line(lx1, ly1, lx2, ly2, z=1, color=(0, 0, 255))
        lx1, ly1 = self.on_screen(-10, 0)
        lx2, ly2 = self.on_screen(10, 0)
        self.add_line(lx1, ly1, lx2, ly2, z=1, color=(0, 0, 255))

        # '''
        total = 0

        qual = self.get_val('qual')
        c = self.get_val('c')
        j = 1j
        for px in range(self.w):
            for py in range(self.h):
                x, y = self.on_plot(px, py)
                z = x + y * j
                i = 0
                while abs(z) < 10 and i < qual:
                    z = z * z + c
                    i += 1
                if i == qual:
                    self.add_point(px, py)
        # '''

        self.flush()

    def key_down(self, symbol, modifiers):
        super().key_down(symbol, modifiers)

    def resize(self, width, height):
        self.refit(width, height - 200)


class JuliaWindow(pyg.window.Window):
    def set_vars(self):
        self.valset.add_value('sz', .5)
        self.valset.add_value('qual', 10)
        self.valset.add_value('c', -1+0j)
        screen = JuliaScreen(0, 200, 500, 500, valset=self.valset)
        self.add_screen('main', screen)
        self.add_int_field('qual', 260, 155, 100, 15, 'Quality', self.valset.get_obj('qual'))
        self.add_complex_field('c', 260, 95, 100, 15, 'C', self.valset.get_obj('c'))
        self.add_button('resetb', 190, 120, 40, 40, 'Reset', self.screens['main'].reset)


window = JuliaWindow(width=500, height=700, caption='Julia Graph', bg=(0, 0, 0, 1), resizable=True)
pyglet.app.run()
