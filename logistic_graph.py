from pyg import *


def dynamic(a, x, i, r):
    for n in range(i):
        x = a * x * (1 - x)
    rl = []
    for n in range(r):
        x = a * x * (1 - x)
        rl.append(x)
    return rl


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
            self.sw = 1
            self.sh = 1
        elif self.mode == 1:
            self.sx = 0.5
            self.sy = 0.5
            self.sw = 1
            self.sh = 1
        self.render()

    def zoomup(self):
        if self.sz < 1:
            self.sz += 0.1

    def zoomdown(self):
        if self.sz > 0:
            self.sz -= 0.1

    def setmode(self, m):
        self.mode = m
        self.reset()

    def setvars(self):
        # zoomed to 3.630315,0.769489 with size 0.000015,0.000015
        self.sx = 3.5
        self.sy = .5
        self.sw = 1
        self.sh = 1
        self.sz = .5
        self.mode = 0 # 0-bifurcation 1-cobweb

    def render(self):
        if self.mode == 0:
            for px in range(self.w):
                # a = px * 1 / self.width + 3
                a = px * self.sw / self.h + self.sx - self.sw / 2
                orbit = dynamic(a, 0.1, 1000, 200)
                for py in orbit:
                    # ppy = py * self.height
                    ppy = (py - self.sy + self.sh / 2) * self.h / self.sh
                    if ppy < 0 or ppy > self.h:
                        continue
                    self.add_point(px + .5, ppy + .5)
            print(str(len(self.vertexes['points']) // 3) + ' points')
        elif self.mode == 1:
            pass
        self.flush()

    def on_resize(self, width, height):
        self.w = width
        self.h = height - 200
        self.setbg(self.bg)

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

        zoomlabel = pyglet.text.Label('Zoom: %.1f' % self.screens[0].sz, font_name='Verdana', font_size=8, x=30, y=50)
        self.labels.append(zoomlabel)
        zupb = Button(90, 50, 40, 40, 'Zoom+', self.zoomup)
        self.buttons.append(zupb)
        zdownb = Button(140, 50, 40, 40, 'Zoom-', self.zoomdown)
        self.buttons.append(zdownb)

        m1b = Button(300, 150, 100, 40, 'Bifurcation Graph', lambda: self.screens[0].setmode(0))
        self.buttons.append(m1b)
        m2b = Button(300, 100, 100, 40, 'Cobweb Diagram', lambda: self.screens[0].setmode(1))
        self.buttons.append(m2b)

    def zoomup(self):
        self.screens[0].zoomup()
        self.redraw_labels()

    def zoomdown(self):
        self.screens[0].zoomdown()
        self.redraw_labels()

    def redraw_labels(self):
        for label in self.labels:
            label.delete()
            self.labels.remove(label)
        zoomlabel = pyglet.text.Label('Zoom: %.1f' % self.screens[0].sz, font_name='Verdana', font_size=8, x=30, y=50)
        self.labels.append(zoomlabel)

        self.on_draw()


window = GraphWindow(width=600, height=800, caption='Logistics Graph', bg=(0, 0, 0, 1), resizable=True)
pyglet.app.run()
