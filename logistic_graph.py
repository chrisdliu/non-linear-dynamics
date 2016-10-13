from pyg import *


def dynamic(a, x, trans, iter):
    for n in range(trans):
        x = a * x * (1 - x)
    result = []
    for n in range(iter):
        x = a * x * (1 - x)
        result.append(x)
    return result


def next(a, x):
    return a * x * (1 - x)


class GraphScreen(Screen):
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
        self.render()

    def zoomup(self):
        if self.sz < 1:
            self.sz += 0.1

    def zoomdown(self):
        if self.sz > 0:
            self.sz -= 0.1

    def cobtoggle(self):
        if self.mode == 1:
            self.runcobweb = not self.runcobweb
            if self.runcobweb:
                self.resetcobweb()

    def setmode(self, m):
        self.mode = m
        if self.mode != 1:
            self.runcobweb = False
        self.reset()

    def setvars(self):
        # zoomed to 3.630315,0.769489 with size 0.000015,0.000015
        self.sx = 3.5
        self.sy = .5
        self.sw = 1
        self.sh = 1
        self.sz = .5
        self.a = 4
        self.runcobweb = False
        self.cobwebframe = []
        self.fpoints = []
        self.mode = 0 # 0-bifurcation 1-cobweb
        self.setmode(1)
        self.setfpoints()

    def setfpoints(self):
        self.fpoints.clear()
        for px in range(self.w):
            x = px * self.sw / self.w + self.sx - self.sw / 2
            y = self.a * x * (1 - x)
            py = (y - self.sy + self.sh / 2) * self.h / self.sh
            self.fpoints.append((px, py))

    def resetcobweb(self):
        self.cobwebframe = [.234, next(self.a, .234)]

    def tick(self):
        if self.runcobweb:
            self.cobwebframe.append(next(self.a, self.cobwebframe[-1]))
            if len(self.cobwebframe) > 16:
                self.cobwebframe.pop(0)
            self.render()

    def render(self):
        if self.mode == 0:
            for px in range(self.w):
                # a = px * 1 / self.width + 3
                a = px * self.sw / self.w + self.sx - self.sw / 2
                orbit = dynamic(a, 0.1, 1000, 200)
                for py in orbit:
                    # ppy = py * self.height
                    ppy = (py - self.sy + self.sh / 2) * self.h / self.sh
                    if ppy < 0 or ppy > self.h:
                        continue
                    self.add_point(px + .5, ppy + .5)
            print(str(len(self.vertexes['points']) // 3) + ' points')
        elif self.mode == 1:
            self.setfpoints()
            lx1, ly1 = self.onplot(0, 0)
            lx2, ly2 = self.onplot(1, 1)
            self.add_line(lx1, ly1, lx2, ly2)
            for px, py in self.fpoints:
                self.add_point(px, py)
            if not self.runcobweb:
                orbit = dynamic(self.a, 0.1, 0, 25)
                for i in range(len(orbit) - 1):
                    x1, y1 = self.onplot(orbit[i], orbit[i])
                    x2, y2 = self.onplot(orbit[i], orbit[i + 1])
                    x3, y3 = self.onplot(orbit[i + 1], orbit[i + 1])
                    self.add_line(x1, y1, x2, y2)
                    self.add_line(x2, y2, x3, y3)
            else:
                for i in range(len(self.cobwebframe) - 1):
                    x1, y1 = self.onplot(self.cobwebframe[i], self.cobwebframe[i])
                    x2, y2 = self.onplot(self.cobwebframe[i], self.cobwebframe[i + 1])
                    x3, y3 = self.onplot(self.cobwebframe[i + 1], self.cobwebframe[i + 1])
                    self.add_line(x1, y1, x2, y2, color=(-i * 17 - 1, 0, 0))
                    self.add_line(x2, y2, x3, y3, color=(-i * 17 - 1, 0, 0))

        self.flush()

    def on_resize(self, width, height):
        self.sw = self.sw * (width / self.w)
        self.sh = self.sh * ((height - 200) / self.h)
        self.w = width
        self.h = height - 200
        self.setbg(self.bg)
        if self.mode == 1:
            self.setfpoints()

    def mouse_up(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT:
            self.sx = self.sx - self.sw / 2 + x * self.sw / self.w
            self.sy = self.sy - self.sh / 2 + y * self.sh / self.h
            self.sw *= self.sz
            self.sh *= self.sz
        elif button == pyglet.window.mouse.RIGHT:
            self.sx = self.sx - self.sw / 2 + x * self.sw / self.w
            self.sy = self.sy - self.sh / 2 + y * self.sh / self.h
            self.sw /= self.sz
            self.sh /= self.sz
        print('zoomed to %f,%f with size %f,%f' % (self.sx, self.sy, self.sw, self.sh))
        self.render()


class GraphWindow(Window2):
    def setvars(self):
        self.screens.append(GraphScreen(0, 200, 600, 600))

        upb = Button(75, 145, 40, 40, 'Up', self.screens[0].up)
        self.buttons.append(upb)
        downb = Button(75, 100, 40, 40, 'Down', self.screens[0].down)
        self.buttons.append(downb)
        leftb = Button(30, 120, 40, 40, 'Left', self.screens[0].left)
        self.buttons.append(leftb)
        rightb = Button(120, 120, 40, 40, 'Right', self.screens[0].right)
        self.buttons.append(rightb)
        resetb = Button(180, 120, 40, 40, 'Reset', self.screens[0].reset)
        self.buttons.append(resetb)

        zupb = Button(90, 50, 40, 40, 'Zoom+', self.zoomup)
        self.buttons.append(zupb)
        zdownb = Button(140, 50, 40, 40, 'Zoom-', self.zoomdown)
        self.buttons.append(zdownb)

        m1b = Button(300, 150, 100, 40, 'Bifurcation Graph', lambda: self.screens[0].setmode(0))
        self.buttons.append(m1b)
        m2b = Button(300, 100, 100, 40, 'Cobweb Diagram', lambda: self.screens[0].setmode(1))
        self.buttons.append(m2b)

        runcob = Button(410, 100, 80, 40, 'Run Cobweb', self.screens[0].cobtoggle)
        self.buttons.append(runcob)

        self.redraw_labels()

    def zoomup(self):
        self.screens[0].zoomup()
        # self.redraw_labels()

    def zoomdown(self):
        self.screens[0].zoomdown()
        # self.redraw_labels()

    def redraw_labels(self):
        for label in self.labels:
            label.delete()
        self.labels.clear()
        zoomlabel = pyglet.text.Label('Zoom: %.1f' % self.screens[0].sz, font_name='Verdana', font_size=8, x=30, y=50)
        self.labels.append(zoomlabel)
        leftlabel = pyglet.text.Label('%.5f' % (self.screens[0].sx - self.screens[0].sw / 2), font_name='Verdana', font_size=8, x=10, y=190)
        self.labels.append(leftlabel)
        rightlabel = pyglet.text.Label('%.5f' % (self.screens[0].sx + self.screens[0].sw / 2), font_name='Verdana', font_size=8, x=self.screens[0].w - 60, y=190)
        self.labels.append(rightlabel)


window = GraphWindow(width=600, height=800, caption='Logistics Graph', bg=(0, 0, 0, 1), resizable=True)
pyglet.app.run()
