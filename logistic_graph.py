"""
By Chris Liu

Requires pyglet and pyg to run

How to use:
Left click to zoom in
Right click to zoom out
Hold middle mouse and move mouse to move the screen
Click to use buttons
Click to select fields, type to enter characters, enter to parse input
Arrow keys can also move the screen in the corresponding direction
"""

import time

import pyglet

import pyg


def get_orbit(a, x, trans, iter):
    """
    Generates an orbit for an a value and starting x value
    :param a: a
    :param x: x
    :param trans: number of transients
    :param iter: number of iterations to return
    :return: the orbit
    """
    for n in range(trans):
        x = a * x * (1 - x)
    result = [x, ]
    for n in range(iter):
        x = a * x * (1 - x)
        result.append(x)
    return result


def get_next(a, x):
    """
    Returns the next value in the orbit
    :param a: a
    :param x: x
    :return: the next value
    """
    return a * x * (1 - x)


class LogisticScreen(pyg.screen.GraphScreen):
    def __init__(self, x, y, width, height, valset, zoom_valobj, bg=(255, 255, 255)):
        self.mode = 0  # 0-bifurcation 1-cobweb 2-time series
        super().__init__(x, y, width, height, .5, .5, 1, 1, valset, zoom_valobj, bg=bg)
        self.runcobweb = False
        self.cobwebframe = []
        self.fpoints = []
        self.setfpoints()
        self.set_mode(1, None)

        # 3.630315,0.769489 @ 0.000015,0.000015

    def set_mode(self, m, buttons):
        """
        Sets the mode: 0-bifurcation 1-cobweb 2-time series
        :param m: the mode
        :param buttons: the window's buttons
        """
        self.mode = m
        if m == 0:
            self.reset_to(3.5, .5, 1, 1)
        elif m == 1:
            self.reset_to(.5, .5, 1, 1)
        else:
            self.reset_to(300, .5, 600, 1)
        if self.mode != 1:
            self.runcobweb = False
            buttons['runcob'].set_text('Run')
        self.reset_screen()


    def cobtoggle(self, button):
        """
        Toggles the running cob diagram
        :param button: the button that triggers it
        """
        if self.mode == 1:
            self.runcobweb = not self.runcobweb
            if self.runcobweb:
                self.resetcobweb()
                button.set_text('Stop')
            else:
                button.set_text('Run')

    def resetcobweb(self):
        """
        Resets the running cob diagram
        """
        self.cobwebframe = [self.get_val('startx'), get_next(self.get_val('a'), self.get_val('startx'))]

    def setfpoints(self):
        """
        Sets the points of the function ax(1-x)
        """
        self.fpoints.clear()
        for px in range(self.w):
            x, _ = self.on_plot(px, 0)
            if x < 0 or x > 1:
                continue
            y = self.get_val('a') * x * (1 - x)
            _, py = self.on_screen(0, y)
            self.fpoints.append((px, py))

    def tick(self):
        """
        Ticks the cobweb if running
        """
        if self.runcobweb:
            self.cobwebframe.append(get_next(self.get_val('a'), self.cobwebframe[-1]))
            if len(self.cobwebframe) > self.get_val('cob-tail'):
                self.cobwebframe.pop(0)
            self.render()

    def render(self):
        """
        Renders everything
        """
        start = time.clock()

        if self.mode == 0:
            for px in range(self.w):
                a, _ = self.on_plot(px, 0)
                orbit = get_orbit(a, self.get_val('startx'), self.get_val('bif-trans'), self.get_val('bif-iter'))
                for y in orbit:
                    # ppy = py * self.height
                    _, py = self.on_screen(0, y)
                    if py < 0 or y > self.h:
                        continue
                    self.add_point(px, py)
            print(str(len(self._vertexes['points']) // 3) + ' points')
        elif self.mode == 1:
            # y = x
            lx1, ly1 = self.on_screen(-10, -10)
            lx2, ly2 = self.on_screen(10, 10)
            self.add_line(lx1, ly1, lx2, ly2, color=(0, 255, 0))
            # y = 0
            lx1, ly1 = self.on_screen(-10, 0)
            lx2, ly2 = self.on_screen(10, 0)
            self.add_line(lx1, ly1, lx2, ly2, color=(0, 0, 255))
            # x = 0
            lx1, ly1 = self.on_screen(0, -10)
            lx2, ly2 = self.on_screen(0, 10)
            self.add_line(lx1, ly1, lx2, ly2, color=(0, 0, 255))
            # draws curve
            self.setfpoints()
            for px, py in self.fpoints:
                self.add_point(px, py)
            if not self.runcobweb:
                orbit = get_orbit(self.get_val('a'), self.get_val('startx'), self.get_val('cob-trans'), self.get_val('cob-iter'))
                for i in range(len(orbit) - 1):
                    x1, y1 = self.on_screen(orbit[i], orbit[i])
                    x2, y2 = self.on_screen(orbit[i], orbit[i + 1])
                    x3, y3 = self.on_screen(orbit[i + 1], orbit[i + 1])
                    self.add_line(x1, y1, x2, y2)
                    self.add_line(x2, y2, x3, y3)
            else:
                for i in range(len(self.cobwebframe) - 1):
                    x1, y1 = self.on_screen(self.cobwebframe[i], self.cobwebframe[i])
                    x2, y2 = self.on_screen(self.cobwebframe[i], self.cobwebframe[i + 1])
                    x3, y3 = self.on_screen(self.cobwebframe[i + 1], self.cobwebframe[i + 1])
                    self.add_line(x1, y1, x2, y2, color=(-i * 17 - 1, 0, 0))
                    self.add_line(x2, y2, x3, y3, color=(-i * 17 - 1, 0, 0))
        elif self.mode == 2:
            # y = 0
            lx1, ly1 = self.on_screen(0, 0)
            lx2, ly2 = self.on_screen(10000, 0)
            self.add_line(lx1, ly1, lx2, ly2, color=(0, 0, 255))
            # x = 0
            lx1, ly1 = self.on_screen(0, 0)
            lx2, ly2 = self.on_screen(0, 1)
            self.add_line(lx1, ly1, lx2, ly2, color=(0, 0, 255))
            # draw dots
            y = self.get_val('startx')
            for n in range(int(self.max_gx)):
                px, py = self.on_screen(n, y)
                self.add_point(px, py)
                y = get_next(self.get_val('a'), y)

        end = time.clock()
        #print('render time: ' + str((end - start) * 1000) + ' ms')
        self.flush()

    def resize(self, width, height):
        """
        Resizes screen when window is resized
        :param width: width
        :param height: height
        """
        self.refit(width, height - 200)



class LogisticWindow(pyg.window.Window):
    def set_vars(self):
        """
        Sets values and objects of the window
        """
        # values
        self.valset.add_float_value('sz', .5, limit='ul', inclusive='', low=0, high=1)
        self.valset.add_float_value('a', 1, limit='ul', low=0, high=4)
        self.valset.add_float_value('startx', .802, limit='ul', low=0, high=1)
        self.valset.add_int_value('bif-trans', 1000)
        self.valset.add_int_value('bif-iter', 200)
        self.valset.add_int_value('cob-trans', 0)
        self.valset.add_int_value('cob-iter', 25)
        self.valset.add_int_value('cob-tail', 25)

        # screen
        self.add_screen('main', (LogisticScreen(0, 200, 600, 600, self.valset, self.get_valobj('sz'))))

        # fields
        self.add_float_field('zoomfield', 30, 60, 100, 15, 'Zoom', self.get_valobj('sz'))
        self.add_float_field('a', 260, 155, 100, 15, 'A', self.get_valobj('a'))
        self.add_float_field('startx', 260, 135, 100, 15, 'Xo', self.get_valobj('startx'))
        self.add_int_field('bif-trans', 445, 155, 100, 15, 'Bif Trans', self.get_valobj('bif-trans'))
        self.add_int_field('bif-iter', 445, 135, 100, 15, 'Bif Iter', self.get_valobj('bif-iter'))
        self.add_int_field('cob-trans', 445, 105, 100, 15, 'Cob Trans', self.get_valobj('cob-trans'))
        self.add_int_field('cob-iter', 445, 85, 100, 15, 'Cob Iter', self.get_valobj('cob-iter'))
        self.add_int_field('cob-tail', 445, 65, 100, 15, 'Cob Tail', self.get_valobj('cob-tail'))

        # buttons
        self.add_button('upb', 75, 145, 40, 40, 'Up', self.screens['main'].up)
        self.add_button('downb', 75, 100, 40, 40, 'Down', self.screens['main'].down)
        self.add_button('leftb', 30, 120, 40, 40, 'Left', self.screens['main'].left)
        self.add_button('rightb', 120, 120, 40, 40, 'Right', self.screens['main'].right)
        self.add_button('resetb', 190, 120, 40, 40, 'Reset', self.screens['main'].reset_screen)
        self.add_button('m1b', 370, 130, 65, 40, 'Bifurcation', lambda: self.screens['main'].set_mode(0, self.buttons))
        self.add_button('m2b', 370, 80, 65, 40, 'Cobweb', lambda: self.screens['main'].set_mode(1, self.buttons))
        self.add_button('m3b', 370, 30, 65, 40, 'Time Series', lambda: self.screens['main'].set_mode(2, self.buttons))
        self.add_button('runcob', 320, 80, 40, 40, 'Run', lambda: self.screens['main'].cobtoggle(self.buttons['runcob']))

        # labels
        self.add_label('leftlabel', 10, 180, '%.5f' % self.get_screen('main').min_gx, color=(255, 0, 255))
        self.add_label('rightlabel', self.screens['main'].w - 60, 180, '%.5f' % self.get_screen('main').max_gx, color=(255, 0, 255))
        self.add_label('toplabel', 10, self.screens['main'].h + 180, '%.5f' % self.get_screen('main').max_gy, color=(255, 0, 255))
        self.add_label('bottomlabel', 10, 210, '%.5f' % self.get_screen('main').min_gy, color=(255, 0, 255))

    def update_labels(self):
        """
        Updates the labels
        """
        self.labels['leftlabel'].set_text('%.5f' % self.get_screen('main').min_gx)
        self.labels['rightlabel'].set_text('%.5f' % self.get_screen('main').max_gx)
        self.labels['rightlabel'].set_pos(self.screens['main'].w - 60, 180)
        self.labels['toplabel'].set_text('%.5f' % self.get_screen('main').max_gy)
        self.labels['toplabel'].set_pos(10, self.screens['main'].h + 180)
        self.labels['bottomlabel'].set_text('%.5f' % self.get_screen('main').min_gy)


window = LogisticWindow(width=600, height=800, caption='Logistics Graph', bg=(0, 0, 0, 1), resizable=True)
pyglet.app.run()
