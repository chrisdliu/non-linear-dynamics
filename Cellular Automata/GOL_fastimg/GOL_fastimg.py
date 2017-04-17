import pyg

import numpy as np
from ctypes import *

from pyglet.gl import *
from pyglet.window import key
from pyglet import clock

import time


def rdim(x, y, w, h):
    return x, y, x + w, y, x + w, y + h, x, y + h


def printworld(world):
    for x in range(len(world) - 2, 0, -1):
        print(x, end='')
        for y in range(1, len(world[0]) - 1):
            if world[x][y]:
                print('*', end='')
            else:
                print('-', end='')
        print()
    print()


class GOLScreen(pyg.screen.Screen2D):
    def __init__(self, *args):
        super().__init__(*args)

        self.gen = 0

        # clib setup
        self.clib = cdll.LoadLibrary('clib_fastimg.so')

        self.wr = 1003
        self.wc = 1003
        # world center
        self.wcx = 21
        self.wcy = 21
        # square size
        self.wss = 4

        c_ubyte_p_array = POINTER(c_ubyte) * self.wr

        self.world = np.random.randint(2, size=(self.wr, self.wc), dtype=np.ubyte)
        for i in range(self.wr):
            self.world[i][0] = 0
            self.world[i][self.wc - 1] = 0
        for i in range(self.wc):
            self.world[0][i] = 0
            self.world[self.wr - 1][i] = 0
        self.alt = np.copy(self.world)
        world_p = np.ctypeslib.as_ctypes(self.world)
        alt_p = np.ctypeslib.as_ctypes(self.alt)
        self.world_pp = c_ubyte_p_array(*world_p)
        self.alt_pp = c_ubyte_p_array(*alt_p)
        self.swap = False

        lookup = np.empty(512, dtype=np.ubyte)
        for i in range(512):
            count = sum([i >> j & 1 for j in range(1, 9)])
            if i % 2:
                if 1 < count < 4:
                    lookup[i] = 1
                else:
                    lookup[i] = 0
            else:
                if count == 3:
                    lookup[i] = 1
                else:
                    lookup[i] = 0
        self.lookup_p = np.ctypeslib.as_ctypes(lookup)

        # img setup
        self.pixels = np.full(self.w * self.h * 3, 255, dtype=np.ubyte)
        self.pixels_p = np.ctypeslib.as_ctypes(self.pixels)
        self.clib.set_pixels(self.world_pp, self.wr, self.wc, self.pixels_p, self.w, self.h,
                             self.wss, self.wcx, self.wcy)
        self.img = pyglet.image.ImageData(self.w, self.h, 'RGB', self.pixels_p)

    def draw(self):
        self.img.blit(self.x, self.y)

    def tick(self, dt):
        start = time.time()
        self.clib.turn(self.world_pp, self.alt_pp, self.swap, self.wr, self.wc, 1, self.lookup_p, self.pixels_p,
                       self.w, self.h, self.wss, self.wcx, self.wcy)
        self.img.set_data('RGB', self.img.width * 3, self.pixels_p)

        self.swap = not self.swap
        self.gen += 1

        self.draw()
        end = time.time()

        self.set_val('ticktime', (end - start) * 1000)
        self.set_val('dt', dt)

    def key_down(self, symbol, modifiers):
        if symbol == key.LEFT:
            self.wcx -= 5
            if self.wcx < 1:
                self.wcx = 1
        elif symbol == key.RIGHT:
            self.wcx += 5
            if self.wcx > self.wc - 2:
                self.wcx = self.wc - 2
        elif symbol == key.UP:
            self.wcy += 5
            if self.wcy > self.wr - 2:
                self.wcy = self.wr - 2
        elif symbol == key.DOWN:
            self.wcy -= 5
            if self.wcy < 1:
                self.wcy = 1
        elif symbol == key.A:
            if self.wss > 2:
                self.wss -= 2
        elif symbol == key.S:
            self.wss += 2

        self.clib.set_pixels(self.world_pp, self.wr, self.wc, self.pixels_p, self.w, self.h,
                             self.wss, self.wcx, self.wcy)
        self.img.set_data('RGB', self.img.width * 3, self.pixels_p)

    def randomize(self):
        del self.world, self.world_pp, self.alt, self.alt_pp

        self.gen = 0

        c_ubyte_p_array = POINTER(c_ubyte) * self.wr

        self.world = np.random.randint(2, size=(self.wr, self.wc), dtype=np.ubyte)
        for i in range(self.wr):
            self.world[i][0] = 0
            self.world[i][self.wc - 1] = 0
        for i in range(self.wc):
            self.world[0][i] = 0
            self.world[self.wr - 1][i] = 0
        self.alt = np.copy(self.world)
        world_p = np.ctypeslib.as_ctypes(self.world)
        alt_p = np.ctypeslib.as_ctypes(self.alt)
        self.world_pp = c_ubyte_p_array(*world_p)
        self.alt_pp = c_ubyte_p_array(*alt_p)
        self.swap = False

        self.clib.set_pixels(self.world_pp, self.wr, self.wc, self.pixels_p, self.w, self.h,
                             self.wss, self.wcx, self.wcy)
        self.img.set_data('RGB', self.img.width * 3, self.pixels_p)

        self.draw()

    def resize(self, width, height):
        self.set_size(width - 200, height)

        del self.pixels, self.pixels_p, self.img

        self.pixels = np.full(self.w * self.h * 3, 255, dtype=np.ubyte)
        self.pixels_p = np.ctypeslib.as_ctypes(self.pixels)
        self.clib.set_pixels(self.world_pp, self.wr, self.wc, self.pixels_p, self.w, self.h,
                             self.wss, self.wcx, self.wcy)
        self.img = pyglet.image.ImageData(self.w, self.h, 'RGB', self.pixels_p)


class GOLWindow(pyg.window.Window):
    def set_vars(self):
        self.add_float_value('gz', .75, limit='ul', inclusive='', low=0, high=1)
        self.add_screen('1', GOLScreen(self, 200, 0, 600, 600))

        self.add_label('genlabel', 20, 10, color=(255, 0, 255))
        self.add_float_value('dt', 1)
        self.add_label('speedlabel', 20, 30, color=(255, 0, 255))
        self.add_label('dtlabel', 20, 50, color=(255, 0, 255))
        self.add_float_value('ticktime')
        self.add_label('ticklabel', 20, 70, color=(255, 0, 255))

        self.running = False
        self.add_button('start', 20, 100, 40, 25, 'Start', self.start)
        self.add_button('stop', 70, 100, 40, 25, 'Stop', self.stop)
        self.add_button('randomize', 120, 100, 60, 25, 'Randomize', self.randomize)

        self.add_int_value('speed', 50, limit='l', low=1)
        self.add_int_field('speed', 20, 80, 140, 15, 'Speed (gen/s)', self.get_valobj('speed'))

    def update_labels(self):
        self.labels['genlabel'].set_text('Generation %d' % self.screens['1'].gen)
        self.labels['speedlabel'].set_text('%s gen/s' % str(round(1 / self.get_val('dt'), 2)))
        self.labels['dtlabel'].set_text('DT: %s' % str(round(self.get_val('dt'), 5)))
        self.labels['ticklabel'].set_text('Ticktime: %sms' % str(round(self.get_val('ticktime'), 2)))

    def start(self):
        if not self.running:
            clock.schedule_interval(self.tick, 1 / self.get_val('speed'))
            self.running = True

    def stop(self):
        if self.running:
            clock.unschedule(self.tick)
            self.running = False

    def tick(self, dt):
        self.screens['1'].tick(dt)

    def randomize(self):
        if not self.running:
            self.screens['1'].randomize()

pyg.run(GOLWindow, 800, 600, 'Game of Life')