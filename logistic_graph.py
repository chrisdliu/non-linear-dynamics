from pyg import *


def get_orbit(a, x, trans, iter):
    for n in range(trans):
        x = a * x * (1 - x)
    result = []
    for n in range(iter):
        x = a * x * (1 - x)
        result.append(x)
    return result


def get_next(a, x):
    return a * x * (1 - x)


class GraphScreen(Screen):
    def __init__(self, x, y, width, height, bg=(255, 255, 255), valset=None):
        super().__init__(x, y, width, height, bg=bg, valset=valset)
        self.runcobweb = False
        self.cobwebframe = []
        self.fpoints = []
        self.setfpoints()
        self.mode = 0 # 0-bifurcation 1-cobweb 2-time series
        self.set_mode(1)

        # zoomed to 3.630315,0.769489 with size 0.000015,0.000015

    def set_mode(self, m):
        self.mode = m
        if self.mode != 1:
            self.runcobweb = False
        self.reset()

    def up(self):
        self.sy += self.sh / 5
        self.render()

    def down(self):
        self.sy -= self.sh / 5
        self.render()

    def left(self):
        self.sx -= self.sw / 5
        self.render()

    def right(self):
        self.sx += self.sw / 5
        self.render()

    def reset(self):
        if self.mode == 0:
            self.sx = 3.5
            self.sy = .5
            self.sw = 1 * (self.w / 600)
            self.sh = 1 * (self.h / 600)
        elif self.mode == 1:
            self.sx = 0.5
            self.sy = 0.5
            self.sw = 1 * (self.w / 600)
            self.sh = 1 * (self.h / 600)
        elif self.mode == 2:
            self.sx = 300
            self.sy = .5
            self.sw = 1 * (self.w / 1)
            self.sh = 1 * (self.h / 600)
        self.render()

    '''
    def zoomup(self):
        if self.sz < 1:
            self.sz += 0.1

    def zoomdown(self):
        if self.sz > 0:
            self.sz -= 0.1
    '''

    def cobtoggle(self):
        if self.mode == 1:
            self.runcobweb = not self.runcobweb
            if self.runcobweb:
                self.resetcobweb()

    def setfpoints(self):
        self.fpoints.clear()
        for px in range(self.w):
            x = px * self.sw / self.w + self.sx - self.sw / 2
            if x < 0 or x > 1:
                continue
            y = self.get_val('a') * x * (1 - x)
            py = (y - self.sy + self.sh / 2) * self.h / self.sh
            self.fpoints.append((px, py))

    def resetcobweb(self):
        self.cobwebframe = [.234, get_next(self.get_val('a'), self.get_val('startx'))]

    def tick(self):
        if self.runcobweb:
            self.cobwebframe.append(get_next(self.get_val('a'), self.cobwebframe[-1]))
            if len(self.cobwebframe) > 16:
                self.cobwebframe.pop(0)
            self.render()

    def render(self):
        if self.mode == 0:
            for px in range(self.w):
                # a = px * 1 / self.width + 3
                a = px * self.sw / self.w + self.sx - self.sw / 2
                orbit = get_orbit(a, self.get_val('startx'), self.get_val('trans'), self.get_val('iter'))
                for py in orbit:
                    # ppy = py * self.height
                    ppy = (py - self.sy + self.sh / 2) * self.h / self.sh
                    if ppy < 0 or ppy > self.h:
                        continue
                    self.add_point(px + .5, ppy + .5)
            print(str(len(self.vertexes['points']) // 3) + ' points')
        elif self.mode == 1:
            # y = x
            lx1, ly1 = self.on_plot(-10, -10)
            lx2, ly2 = self.on_plot(10, 10)
            self.add_line(lx1, ly1, lx2, ly2, color=(0, 255, 0))
            # y = 0
            lx1, ly1 = self.on_plot(-10, 0)
            lx2, ly2 = self.on_plot(10, 0)
            self.add_line(lx1, ly1, lx2, ly2, color=(0, 0, 255))
            # x = 0
            lx1, ly1 = self.on_plot(0, -10)
            lx2, ly2 = self.on_plot(0, 10)
            self.add_line(lx1, ly1, lx2, ly2, color=(0, 0, 255))
            # draws curve
            self.setfpoints()
            for px, py in self.fpoints:
                self.add_point(px, py)
            if not self.runcobweb:
                orbit = get_orbit(self.get_val('a'), self.get_val('startx'), 0, 25)
                for i in range(len(orbit) - 1):
                    x1, y1 = self.on_plot(orbit[i], orbit[i])
                    x2, y2 = self.on_plot(orbit[i], orbit[i + 1])
                    x3, y3 = self.on_plot(orbit[i + 1], orbit[i + 1])
                    self.add_line(x1, y1, x2, y2)
                    self.add_line(x2, y2, x3, y3)
            else:
                for i in range(len(self.cobwebframe) - 1):
                    x1, y1 = self.on_plot(self.cobwebframe[i], self.cobwebframe[i])
                    x2, y2 = self.on_plot(self.cobwebframe[i], self.cobwebframe[i + 1])
                    x3, y3 = self.on_plot(self.cobwebframe[i + 1], self.cobwebframe[i + 1])
                    self.add_line(x1, y1, x2, y2, color=(-i * 17 - 1, 0, 0))
                    self.add_line(x2, y2, x3, y3, color=(-i * 17 - 1, 0, 0))
        elif self.mode == 2:
            # y = 0
            lx1, ly1 = self.on_plot(0, 0)
            lx2, ly2 = self.on_plot(100000, 0)
            self.add_line(lx1, ly1, lx2, ly2, color=(0, 0, 255))
            # x = 0
            lx1, ly1 = self.on_plot(0, 0)
            lx2, ly2 = self.on_plot(0, 1)
            self.add_line(lx1, ly1, lx2, ly2, color=(0, 0, 255))
            yy = self.get_val('startx')
            for n in range(int(self.sx + self.sw / 2)):
                px, py = self.on_plot(n, yy)
                self.add_point(px, py)
                yy = get_next(self.get_val('a'), yy)

        self.flush()

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.sw *= width / self.w
        self.sh *= (height - 200) / self.h
        self.w = width
        self.h = height - 200
        self.set_bg(self.bg)

    def mouse_up(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT:
            self.sx = self.sx - self.sw / 2 + x * self.sw / self.w
            self.sy = self.sy - self.sh / 2 + y * self.sh / self.h
            self.sw *= self.get_val('sz')
            self.sh *= self.get_val('sz')
        elif button == pyglet.window.mouse.RIGHT:
            self.sx = self.sx - self.sw / 2 + x * self.sw / self.w
            self.sy = self.sy - self.sh / 2 + y * self.sh / self.h
            self.sw /= self.get_val('sz')
            self.sh /= self.get_val('sz')
        print('zoomed to %.5f,%.5f with size %.5f,%.5f' % (self.sx, self.sy, self.sw, self.sh))
        self.render()


class GraphWindow(Window):
    def set_vars(self):
        # values and fields
        valset = ValSet()
        valset.add_float('sz', .5)
        valset.add_float('a', 4)
        valset.add_float('startx', .123)
        self.add_float_field('zoomfield', 30, 60, 100, 10, 'Zoom', valset.get_obj('sz'), limit=True, low=0, high=1, inclusive=False)
        self.add_float_field('a', 140, 60, 100, 10, 'A', valset.get_obj('a'), limit=True, low=0, high=4)
        self.add_float_field('startx', 140, 45, 100, 10, 'Xo', valset.get_obj('startx'), limit=True, low=0, high=1)
        valset.add_int('trans', 1000)
        valset.add_int('iter', 200)
        self.add_int_field('trans', 140, 30, 100, 10, 'Trans', valset.get_obj('trans'))
        self.add_int_field('iter', 140, 15, 100, 10, 'Iter', valset.get_obj('iter'))


        # screens
        self.add_screen('main', (GraphScreen(0, 200, 600, 600, valset=valset)))

        # buttons
        self.add_button('upb', 75, 145, 40, 40, 'Up', self.screens['main'].up)
        self.add_button('downb', 75, 100, 40, 40, 'Down', self.screens['main'].down)
        self.add_button('leftb', 30, 120, 40, 40, 'Left', self.screens['main'].left)
        self.add_button('rightb', 120, 120, 40, 40, 'Right', self.screens['main'].right)
        self.add_button('resetb', 220, 120, 40, 40, 'Reset', self.screens['main'].reset)

        # self.add_button('zupb', 120, 30, 40, 40, 'Zoom+', self.zoomup)
        # self.add_button('zdownb', 170, 30, 40, 40, 'Zoom-', self.zoomdown)

        self.add_button('m1b', 300, 150, 65, 40, 'Bifurcation', lambda: self.screens['main'].set_mode(0))
        self.add_button('m2b', 300, 100, 65, 40, 'Cobweb', lambda: self.screens['main'].set_mode(1))
        self.add_button('m3b', 300, 50, 65, 40, 'Time Series', lambda: self.screens['main'].set_mode(2))

        self.add_button('runcob', 370, 100, 40, 40, 'Run', self.cobtoggle)

        # labels
        # self.add_label('zoomlabel', 30, 30, 'Zoom: %.1f' % self.screens['main'].sz)
        self.add_label('leftlabel', 10, 180, '%.5f' % (self.screens['main'].sx - self.screens['main'].sw / 2), color=(255, 0, 255))
        self.add_label('rightlabel', self.screens['main'].w - 60, 180, '%.5f' % (self.screens['main'].sx + self.screens['main'].sw / 2), color=(255, 0, 255))
        self.add_label('toplabel', 10, self.screens['main'].h + 180, '%.5f' % (self.screens['main'].sy + self.screens['main'].sh / 2), color=(255, 0, 255))
        self.add_label('bottomlabel', 10, 210, '%.5f' % (self.screens['main'].sy - self.screens['main'].sh / 2), color=(255, 0, 255))

        self.update_labels()

    def update_labels(self):
        # self.labels['zoomlabel'].set_text('Zoom: %.1f' % self.screens['main'].sz)
        self.labels['leftlabel'].set_text('%.5f' % (self.screens['main'].sx - self.screens['main'].sw / 2))
        self.labels['rightlabel'].set_text('%.5f' % (self.screens['main'].sx + self.screens['main'].sw / 2))
        self.labels['rightlabel'].set_pos(self.screens['main'].w - 60, 180)
        self.labels['toplabel'].set_text('%.5f' % (self.screens['main'].sy + self.screens['main'].sh / 2))
        self.labels['toplabel'].set_pos(10, self.screens['main'].h + 180)
        self.labels['bottomlabel'].set_text('%.5f' % (self.screens['main'].sy - self.screens['main'].sh / 2))

    def cobtoggle(self):
        if self.screens['main'].mode == 1:
            self.screens['main'].cobtoggle()
            if self.screens['main'].runcobweb:
                self.buttons['runcob'].set_text('Stop')
            else:
                self.buttons['runcob'].set_text('Run')

    '''
    def zoomup(self):
        self.screens['main'].zoomup()

    def zoomdown(self):
        self.screens['main'].zoomdown()
    '''


window = GraphWindow(width=600, height=800, caption='Logistics Graph', bg=(0, 0, 0, 1), resizable=True)
pyglet.app.run()
