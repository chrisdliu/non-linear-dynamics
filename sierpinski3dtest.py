from pyglet.gl import *
from pyglet.graphics import Batch
from pyglet.window import key

from vmath import *
import random

WINDOW = 600
INCREMENT = 5


class Window(pyglet.window.Window):
    xRot = yRot = zRot = 0
    dist = 0

    def __init__(self, width, height, title=''):
        super().__init__(width, height, title, resizable=True)
        glClearColor(0, 0, 0, 1)
        glEnable(GL_DEPTH_TEST)

        self.batch = Batch()
        self.vlist = None
        self.set_vlist()

    def set_vlist(self):
        srtos = (1 / 6) * 3 ** .5
        srsot = (1 / 3) * 6 ** .5
        s = 100
        self.offsz = srsot * s * (1 / 3)

        tri = (Vector(srtos * 2 * s, 0, 0),
               Vector(-srtos * s, s * .5, 0),
               Vector(-srtos * s, -s * .5, 0),
               Vector(0, 0, srsot * s))
        p = Vector(0, 0, srsot * s)

        palette = ((255, 0, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255))
        points = []
        colors = []

        for i in range(50000):
            r = random.randrange(4)
            p = (p + tri[r]) / 2
            points.extend(p)
            colors.extend(palette[r])

        self.vlist = self.batch.add(len(points) // 3, GL_POINTS, None, ('v3f', points), ('c3B', colors))

    def on_draw(self):
        self.clear()

        glPushMatrix()

        glTranslatef(0, 0, self.dist)
        glRotatef(self.xRot, 1, 0, 0)
        glRotatef(self.yRot, 0, 1, 0)
        glRotatef(self.zRot, 0, 0, 1)
        glTranslatef(0, 0, -self.offsz)

        self.batch.draw()

        glPopMatrix()

    def on_resize(self, width, height):
        glViewport(0, 0, width, height)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        ar = width / height
        gluPerspective(60, ar, 1, 1000)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0, 0, -400)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.UP:
            self.xRot -= INCREMENT
        elif symbol == key.DOWN:
            self.xRot += INCREMENT
        elif symbol == key.LEFT:
            self.yRot -= INCREMENT
        elif symbol == key.RIGHT:
            self.yRot += INCREMENT
        elif symbol == key.X:
            self.zRot += INCREMENT
        elif symbol == key.Z:
            self.zRot -= INCREMENT
        elif symbol == key.S:
            self.dist += INCREMENT * 10
        elif symbol == key.A:
            self.dist -= INCREMENT * 10


if __name__ == '__main__':
    Window(WINDOW, WINDOW, 'Sierpinski 3D')
    pyglet.app.run()