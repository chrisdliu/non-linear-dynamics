import pyg
import pyglet


class ComplexScreen(pyg.screen.GraphScreen):
    def reset(self):
        self.sx = 0
        self.sy = 0
        self.sw = 10
        self.sh = 10

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
        if symbol == pyglet.window.key.K:
            self.get_obj('n').incr()
            self.render()
        elif symbol == pyglet.window.key.J:
            self.get_obj('n').decr()
            self.render()
        # cProfile.run('window.screens[\'main\'].render()')

    def resize(self, width, height):
        self.refit(width, height - 200)


class ComplexWindow(pyg.window.Window):
    def set_vars(self):
        self.valset.add_value('sz', .5)
        self.valset.add_value('n', 0)
        self.valset.add_value('power', 2)
        self.valset.add_value('hqw', 100)
        self.valset.add_value('c', 0+0j)
        screen = ComplexScreen(0, 200, 500, 500, valset=self.valset)
        self.add_screen('main', screen)
        self.add_int_field('n', 260, 115, 100, 15, 'N', self.valset.get_obj('n'), limit='l', low=0)
        self.add_float_field('power', 260, 135, 100, 15, 'Power', self.valset.get_obj('power'), limit='l', inclusive='', low=0)
        self.add_int_field('hqw', 260, 155, 100, 15, 'Quality', self.valset.get_obj('hqw'))
        self.add_complex_field('c', 260, 95, 100, 15, 'C', self.valset.get_obj('c'))


window = ComplexWindow(width=500, height=700, caption='Complex Graph', bg=(0, 0, 0, 1), resizable=True)
pyglet.app.run()