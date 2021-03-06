import pyglet
import pyg


class ComplexScreen(pyg.screen.GraphScreen):
    def render(self):
        lx1, ly1 = self.on_screen(0, -10)
        lx2, ly2 = self.on_screen(0, 10)
        self.add_line(lx1, ly1, lx2, ly2, z=1, color=(0, 0, 255))
        lx1, ly1 = self.on_screen(-10, 0)
        lx2, ly2 = self.on_screen(10, 0)
        self.add_line(lx1, ly1, lx2, ly2, z=1, color=(0, 0, 255))

        # '''
        j = 1j
        hqw = self.get_val('hqw')
        for qx in range(hqw * 2 + 1):
            for qy in range(hqw * 2 + 1):
                z = ((qx - hqw) / hqw) + ((qy - hqw) / hqw) * j
                ovf = False
                power = self.get_val('power')
                c = self.get_val('c')
                for i in range(self.get_val('n')):
                    try:
                        z **= power
                        z += c
                    except OverflowError:
                        ovf = True
                if ovf:
                    continue
                px, py = self.on_screen(z.real, z.imag)
                self.add_point(px, py)
        # '''

        self.flush()

    def key_down(self, symbol, modifiers):
        super().key_down(symbol, modifiers)
        if symbol == pyglet.window.key.K:
            self.get_valobj('n').incr()
            self.render()
        elif symbol == pyglet.window.key.J:
            self.get_valobj('n').decr()
            self.render()

    def resize(self, width, height):
        self.refit(width, height - 200)


class ComplexWindow(pyg.window.Window):
    def set_vars(self):
        self.add_float_value('sz', .5)
        self.add_int_value('n', 0, limit='l', low=0)
        self.add_float_value('power', 2, limit='l', inclusive='', low=0)
        self.add_int_value('hqw', 100)
        self.add_complex_value('c', 0+0j)
        screen = ComplexScreen(0, 200, 500, 500, 0, 0, 5, 5, self.valset, self.get_valobj('sz'))
        self.add_screen('main', screen)
        self.add_int_field('n', 260, 115, 100, 15, 'N', self.valset.get_valobj('n'))
        self.add_float_field('power', 260, 135, 100, 15, 'Power', self.valset.get_valobj('power'))
        self.add_int_field('hqw', 260, 155, 100, 15, 'Quality', self.valset.get_valobj('hqw'))
        self.add_complex_field('c', 260, 95, 100, 15, 'C', self.valset.get_valobj('c'))
        self.add_button('resetb', 190, 120, 40, 40, 'Reset', self.screens['main'].reset_screen)

pyg.run(ComplexWindow, 500, 700, 'Complex Graph')