import pyg

import numpy as np
from ctypes import *

from pyglet.gl import *
from pyglet.window import key
from pyglet import clock

import time


def rdim(x, y, w, h):
    return x, y, x + w, y, x + w, y + h, x, y + h


class GOLScreen(pyg.screen.Screen2D):
    def __init__(self, *args):
        super().__init__(*args)

        self.gen = 0

        # clib setup
        self.hashlife = cdll.LoadLibrary('hashlife.so')

        self.hashlife.init.argtypes = []
        self.hashlife.init.restype = c_void_p

        self.hashlife.get_root.argtypes = [c_void_p]
        self.hashlife.get_root.restype = c_void_p

        self.hashlife.run.argtypes = [c_void_p, c_void_p, c_long]
        self.hashlife.run.restype = c_void_p

        self.hashlife.end.argtypes = [c_void_p]
        self.hashlife.end.restype = None

        self.hashlife.set_pixels.argtypes = [c_void_p, c_int, c_int, c_void_p, c_long, c_long, c_int]
        self.hashlife.set_pixels.restype = None

        self.hashlife.node_level.argtypes = [c_void_p]
        self.hashlife.node_level.restype = c_int

        self.hashlife.hashtable_count.argtypes = [c_void_p]
        self.hashlife.hashtable_count.restype = c_int

        # hashlife initialization
        self.hashtable = self.hashlife.init()
        self.root = self.hashlife.get_root(self.hashtable)
        self.level = self.hashlife.node_level(self.root)
        self.min = -(2 ** (self.level - 1))
        self.max = 2 ** (self.level - 1) - 1

        # world parameters
        self.cx = 0
        self.cy = 0
        self.ss = 6

        # img setup
        self.pixels = np.full(self.w * self.h * 3, 255, dtype=np.ubyte)
        self.pixels_p = np.ctypeslib.as_ctypes(self.pixels)
        self.hashlife.set_pixels(self.pixels_p, self.w, self.h, self.root, self.cx, self.cy, self.ss)
        self.img = pyglet.image.ImageData(self.w, self.h, 'RGB', self.pixels_p)

    def __del__(self):
        print('Cleaning up...')
        self.hashlife.end(self.hashtable)

    def draw(self):
        self.img.blit(self.x, self.y)

    def tick(self, dt):
        '''
        start = time.time()
        self.hashlife.turn(self.world_pp, self.alt_pp, self.swap, self.wr, self.wc, 1, self.lookup_p, self.pixels_p,
                           self.w, self.h, self.wss, self.wcx, self.wcy)
        self.img.set_data('RGB', self.img.width * 3, self.pixels_p)

        self.swap = not self.swap
        self.gen += 1

        self.draw()
        end = time.time()

        self.set_val('ticktime', (end - start) * 1000)
        self.set_val('dt', dt)
        '''
        pass

    def run(self, n):
        start = time.time()
        self.root = self.hashlife.run(self.hashtable, self.root, n)
        end = time.time()
        self.level = self.hashlife.node_level(self.root)
        self.min = -(2 ** (self.level - 1))
        self.max = 2 ** (self.level - 1) - 1
        self.gen += n

        self.set_val('turntime', (end - start) * 1000)
        self.set_val('level', self.level)
        self.set_val('states', self.hashlife.hashtable_count(self.hashtable))

        self.hashlife.set_pixels(self.pixels_p, self.w, self.h, self.root, self.cx, self.cy, self.ss)
        self.img.set_data('RGB', self.img.width * 3, self.pixels_p)

    def key_down(self, symbol, modifiers):
        if symbol == key.LEFT:
            self.cx -= 4
            if self.cx < self.min:
                self.cx = self.min
        elif symbol == key.RIGHT:
            self.cx += 4
            if self.cx > self.max:
                self.cx = self.max
        elif symbol == key.UP:
            self.cy += 4
            if self.cy > self.max:
                self.cy = self.max
        elif symbol == key.DOWN:
            self.cy -= 4
            if self.cy < self.min:
                self.cy = self.min
        elif symbol == key.A:
            if self.ss > 2:
                self.ss -= 2
        elif symbol == key.S:
            self.ss += 2

        self.hashlife.set_pixels(self.pixels_p, self.w, self.h, self.root, self.cx, self.cy, self.ss)
        self.img.set_data('RGB', self.img.width * 3, self.pixels_p)

    def resize(self, width, height):
        self.set_size(width - 200, height)

        del self.pixels, self.pixels_p, self.img

        self.pixels = np.full(self.w * self.h * 3, 255, dtype=np.ubyte)
        self.pixels_p = np.ctypeslib.as_ctypes(self.pixels)
        self.hashlife.set_pixels(self.pixels_p, self.w, self.h, self.root, self.cx, self.cy, self.ss)
        self.img = pyglet.image.ImageData(self.w, self.h, 'RGB', self.pixels_p)


class GOLWindow(pyg.window.Window):
    def set_vars(self):
        self.add_screen('1', GOLScreen(self, 200, 0, 600, 600))

        self.add_label('genlabel', 5, 10, color=(255, 0, 255))
        self.add_float_value('dt', 1)
        self.add_label('speedlabel', 5, 25, color=(255, 0, 255))
        self.add_label('dtlabel', 5, 40, color=(255, 0, 255))
        self.add_float_value('ticktime')
        self.add_label('ticklabel', 5, 55, color=(255, 0, 255))

        self.add_float_value('turntime')
        self.add_label('turntime', 5, 85, color=(255, 0, 255))
        self.add_int_value('level')
        self.add_label('level', 5, 100, color=(255, 0, 255))
        self.add_int_value('states')
        self.add_label('states', 5, 115, color=(255, 0, 255))

        self.running = False
        self.add_button('start', 5, 250, 40, 25, 'Start', self.start)
        self.add_button('stop', 55, 250, 40, 25, 'Stop', self.stop)
        self.add_button('run', 105, 250, 40, 25, 'Run', self.run)

        self.add_int_value('speed', 50, limit='l', low=1)
        self.add_int_field('speed', 5, 180, 140, 15, 'Tick Speed (tick/s)', self.get_valobj('speed'))
        self.add_int_value('gens', 1, limit='l', low=1)
        self.add_int_field('gens', 5, 200, 190, 15, 'Gen speed (gen/tick)', self.get_valobj('gens'))

    def update_labels(self):
        self.labels['genlabel'].set_text('Generation %d' % self.screens['1'].gen)
        self.labels['speedlabel'].set_text('%s gen/s' % str(round(1 / self.get_val('dt'), 2)))
        self.labels['dtlabel'].set_text('DT: %s' % str(round(self.get_val('dt'), 5)))
        self.labels['ticklabel'].set_text('Ticktime: %sms' % str(round(self.get_val('ticktime'), 2)))

        self.labels['turntime'].set_text('Turntime: %sms' % str(round(self.get_val('turntime'), 2)))
        self.labels['level'].set_text('World size: 2^%d' % self.get_val('level'))
        self.labels['states'].set_text('Stored states: %d' % self.get_val('states'))

    def start(self):
        if not self.running:
            clock.schedule_interval(self.tick, 1 / self.get_val('speed'))
            self.running = True

    def stop(self):
        if self.running:
            clock.unschedule(self.tick)
            self.running = False

    def run(self):
        self.screens['1'].run(self.get_val('gens'))

    def tick(self, dt):
        self.screens['1'].tick(dt)


pyg.run(GOLWindow, 800, 600, 'Game of Life')