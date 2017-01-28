from pyglet.gl import *
from pyglet.graphics import Batch
from pyglet.window import key

from vmath import *
import random

WINDOW = 600
INCREMENT = 5


class Window(pyglet.window.Window):
    x, y, z = 0, 0, -400
    xRot = yRot = zRot = 0
    dist = 0

    def __init__(self, width, height, title=''):
        super().__init__(width, height, title, resizable=True)
        self.width = width
        self.height = height
        glClearColor(0, 0, 0, 1)
        glEnable(GL_DEPTH_TEST)

        self.batch = Batch()
        self.batch2 = Batch()
        self.vlist = None
        self.set_vlist()
        self.testvlist = self.batch2.add(3, GL_TRIANGLES, None, ('v3f', (50, 0, 100, 100, 0, 100, 50, 75, 100)), ('c3B', (255, 255, 255, 255, 255, 255, 255, 255, 255)))

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

        palette = ((255, 0, 0), (255, 255, 0), (0, 255, 0), (100, 100, 255))
        points = []
        colors = []

        for i in range(100000):
            r = random.randrange(4)
            p = (p + tri[r]) / 2
            points.extend(p)
            colors.extend(palette[r])

        self.vlist = self.batch.add(len(points) // 3, GL_POINTS, None, ('v3f', points), ('c3B', colors))

    def on_draw(self):
        self.clear()


        #glEnable(GL_SCISSOR_TEST)
        #glScissor(100, 100, 50, 50)


        #glMatrixMode(GL_PROJECTION)
        #glLoadIdentity()
        #glOrtho(-200, 200, -200, 200, -200, 200)
        #glMatrixMode(GL_MODELVIEW)
        #self.batch2.draw()

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        ar = self.width / self.height
        gluPerspective(60, ar, .01, 1000)
        glMatrixMode(GL_MODELVIEW)

        glPushMatrix()

        #glTranslatef(self.x, self.y, self.z)
        glTranslatef(0, 0, self.dist - 400)
        glRotatef(self.xRot, 1, 0, 0)
        glRotatef(self.yRot, 0, 1, 0)
        glRotatef(self.zRot, 0, 0, 1)
        glRotatef(45, 0, 1, 0)
        glTranslatef(0, 0, -self.offsz)


        self.batch.draw()
        #self.batch2.draw()

        glPopMatrix()


        #glDisable(GL_SCISSOR_TEST)

    def on_resize(self, width, height):
        super().on_resize(width, height)
        #glViewport(0, 0, width, height)

        #glMatrixMode(GL_PROJECTION)
        #glLoadIdentity()
        #ar = width / height
        #gluPerspective(60, ar, .01, 1000)

        #glMatrixMode(GL_MODELVIEW)
        #glLoadIdentity()
        #glTranslatef(0, 0, 0)
        self.on_draw()

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
            self.dist += INCREMENT * 4
        elif symbol == key.A:
            self.dist -= INCREMENT * 4


if __name__ == '__main__':
    Window(WINDOW, WINDOW, 'Sierpinski 3D')
    pyglet.app.run()