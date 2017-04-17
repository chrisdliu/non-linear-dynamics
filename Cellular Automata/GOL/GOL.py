import pyg

import numpy as np
import ctypes

from pyglet.gl import *
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


class GOLScreen(pyg.screen.GraphScreen):
    def __init__(self, *args):
        super().__init__(*args)

        self.gen = 0

        # clib setup
        self.clib = ctypes.cdll.LoadLibrary('clib.so')

        self.wr = 102
        self.wc = 102

        c_ubyte_p_array = ctypes.POINTER(ctypes.c_ubyte) * self.wr

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

        # grid
        for r in range(self.wr - 2):
            for c in range(self.wc - 2):
                if self.world[r + 1][c + 1]:
                    self.add_quad(*rdim(c * 5, r * 5, 5, 5), color=(255, 0, 255))
                else:
                    self.add_quad(*rdim(c * 5, r * 5, 5, 5), color=(255, 255, 255))
        self._vertex_lists['quads'] = self._batch.add(len(self._vertices['quads']) // 3, GL_QUADS, None,
                                                      ('v3f', self._vertices['quads']),
                                                      ('c3B', self._colors['quads']))

        self.add_line(0, 0, (self.wc - 2) * 5, 0)
        self.add_line(0, 0, 0, (self.wr - 2) * 5)
        self._vertex_lists['lines'] = self._batch.add(len(self._vertices['lines']) // 3, GL_LINES, None,
                                                      ('v3f', self._vertices['lines']),
                                                      ('c3B', self._colors['lines']))

        self._clear()

        # printworld(self.world)

    def tick(self, dt):
        start = time.time()
        self.clib.turn(self.world_pp, self.alt_pp, self.swap, self.wr, self.wc, 1, self.lookup_p)
        end = time.time()

        if self.swap:
            curr = self.world
        else:
            curr = self.alt

        for r in range(self.wr - 2):
            for c in range(self.wc - 2):
                if self.world[r + 1][c + 1] != self.alt[r + 1][c + 1]:
                    i = (r * (self.wc - 2) + c) * 3 * 4
                    if curr[r + 1][c + 1]:
                        self._vertex_lists['quads'].colors[i + 1] = 0
                        self._vertex_lists['quads'].colors[i + 4] = 0
                        self._vertex_lists['quads'].colors[i + 7] = 0
                        self._vertex_lists['quads'].colors[i + 10] = 0
                    else:
                        self._vertex_lists['quads'].colors[i + 1] = 255
                        self._vertex_lists['quads'].colors[i + 4] = 255
                        self._vertex_lists['quads'].colors[i + 7] = 255
                        self._vertex_lists['quads'].colors[i + 10] = 255
        # self.set_val('dt', 1 / dt)
        self.set_val('dt', end - start)

        self.swap = not self.swap
        self.gen += 1
        self.draw()
        # printworld(curr)

    def randomize(self):
        del self.world, self.world_pp, self.alt, self.alt_pp

        self.gen = 0

        c_ubyte_p_array = ctypes.POINTER(ctypes.c_ubyte) * self.wr

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

        self._vertex_lists['quads'].delete()
        self._vertex_lists['lines'].delete()
        del self._vertex_lists['quads'], self._vertex_lists['lines']

        # grid
        for r in range(self.wr - 2):
            for c in range(self.wc - 2):
                if self.world[r + 1][c + 1]:
                    self.add_quad(*rdim(c * 5, r * 5, 5, 5), color=(255, 0, 255))
                else:
                    self.add_quad(*rdim(c * 5, r * 5, 5, 5), color=(255, 255, 255))
        self._vertex_lists['quads'] = self._batch.add(len(self._vertices['quads']) // 3, GL_QUADS, None,
                                                      ('v3f', self._vertices['quads']),
                                                      ('c3B', self._colors['quads']))

        self.add_line(0, 0, (self.wc - 2) * 5, 0)
        self.add_line(0, 0, 0, (self.wr - 2) * 5)
        self._vertex_lists['lines'] = self._batch.add(len(self._vertices['lines']) // 3, GL_LINES, None,
                                                      ('v3f', self._vertices['lines']),
                                                      ('c3B', self._colors['lines']))

        self._clear()

        self.draw()

    def resize(self, width, height):
        self.refit(width - 200, height)


class GOLWindow(pyg.window.Window):
    def set_vars(self):
        self.add_float_value('gz', .75, limit='ul', inclusive='', low=0, high=1)
        self.add_screen('1', GOLScreen(self, 200, 0, 600, 600, 250, 250, 600, 600, 'gz'))

        self.add_float_value('dt', 1)
        self.add_label('dtlabel', 20, 10, color=(255, 0, 255))

        self.add_label('genlabel', 20, 30, color=(255, 0, 255))

        self.running = False
        self.add_button('start', 20, 100, 40, 25, 'Start', self.start)
        self.add_button('stop', 70, 100, 40, 25, 'Stop', self.stop)
        self.add_button('randomize', 120, 100, 60, 25, 'Randomize', self.randomize)

        self.add_int_value('speed', 50, limit='l', low=1)
        self.add_int_field('speed', 20, 80, 140, 15, 'Speed (gen/s)', self.get_valobj('speed'))

    def update_labels(self):
        self.labels['dtlabel'].set_text('%s gen/s' % str(round(self.get_val('dt'), 5)))
        self.labels['genlabel'].set_text('Generation %d' % self.screens['1'].gen)

    def start(self):
        if not self.running:
            clock.schedule_interval(self.tick, 1 / self.get_val('speed'))
            self.running = True

    def stop(self):
        if self.running:
            clock.unschedule(self.tick)
            self.running = False

    def randomize(self):
        if not self.running:
            self.screens['1'].randomize()


pyg.run(GOLWindow, 800, 600, 'Game of Life')