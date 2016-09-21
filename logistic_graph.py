from pyg import *


def dynamic(a, x, i, r):
    for n in range(i):
        x = a*x*(1-x)
    rl = []
    for n in range(r):
        x = a*x*(1-x)
        rl.append(x)
    return rl


class Graph(Window2):
    def setvars(self):
        self.vertex_list = []
        #zoomed to 3.630315,0.769489 with size 0.000015,0.000015
        self.x = 3.5
        self.y = .5
        self.w = 1
        self.h = 1

    def render(self):
        for vlist in self.vertex_list:
            vlist.delete()
            self.vertex_list.remove(vlist)

        points = []
        colors = []
        for px in range(self.width):
            #a = px * 1 / self.width + 3
            a = px * self.w / self.width + self.x - self.w / 2
            pl = dynamic(a, 0.1, 1000, 200)
            for py in pl:
                #ppy = py * self.height
                ppy = (py - self.y + self.h / 2) * self.height / self.h
                if ppy < 0 or ppy > self.height:
                    continue
                points.extend((px, ppy))
                colors.extend((0, 0, 0))
        self.vertex_list.append(self.batch.add(len(points) // 2, GL_POINTS, None, ('v2f', points),
                                          ('c3B', colors)))
        print(str(len(points)) + ' points')

    def mouse_release(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT:
            self.x = self.x - self.w / 2 + x * self.w / self.width
            self.y = self.y - self.h / 2 + y * self.h / self.height
            self.w *= 0.5
            self.h *= 0.5
        elif button == pyglet.window.mouse.RIGHT:
            self.x = self.x - self.w / 2 + x * self.w / self.width
            self.y = self.y - self.h / 2 + y * self.h / self.height
            self.w *= 2
            self.h *= 2
        print('zoomed to %f,%f with size %f,%f' % (self.x, self.y, self.w, self.h))

window = Graph(width=600, height=600, caption='Logistics Graph', bg=(1, 1, 1, 1), resizable=True)
pyglet.app.run()