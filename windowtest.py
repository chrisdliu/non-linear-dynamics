from pyg import *

class Test(Window):
    def setvars(self):
        self.s_vlist = []

    def renderscreen(self):
        for vlist in self.s_vlist:
            vlist.delete()
            self.s_vlist.remove(vlist)
        self.s_vlist.append(self.batch.add(4, GL_QUADS, None, ('v3f', (100, 100, 0, 100, 300, 0, 400, 500, 0, 400, 90, 0)), ('c3B', (255, 255, 255, 240, 0, 0, 0, 240, 0, 0, 0, 240))))

window = Test(width=600, height=800, caption='Test', bg=(230, 0, 230, 1), resizable=True)
pyglet.app.run()