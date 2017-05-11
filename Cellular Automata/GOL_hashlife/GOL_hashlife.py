import pyg

import numpy as np
from ctypes import *

from pyglet.gl import *
from pyglet.window import key
from pyglet import clock

import time
import os, sys, subprocess
import re


class RuleValue(pyg.valset.Value):
    def cast(self, cast_value):
        if isinstance(cast_value, str):
            return cast_value
        else:
            return None

    def is_valid(self, new_value):
        if isinstance(new_value, str) and re.match(r'B[1-8]{1,8}/S[0-8]{1,9}', new_value):
            return True

    def get_flags(self):
        b, s = map(lambda x: x[1:], self.value.split('/'))
        bflags = 0
        for i in range(1, 9):
            if str(i) in b:
                bflags |= 1 << i
        sflags = 0
        for i in range(0, 9):
            if str(i) in s:
                sflags |= 1 << i
        return bflags, sflags


class RuleField(pyg.gui.Field):
    accepted = (
        '0', '1', '2', '3',
        '4', '5', '6', '7',
        '8', 'B', 'S', '/',
    )

    def __init__(self, parent, name, x, y, w, h, field_name, valobj, visible=True, interfaced=False):
        if type(valobj) is not RuleValue:
            raise TypeError('Value object is not a RuleValue!')
        super().__init__(parent, name, x, y, w, h, field_name, valobj, visible, interfaced)


def rdim(x, y, w, h):
    return x, y, x + w, y, x + w, y + h, x, y + h


class GOLScreen(pyg.screen.Screen2D):
    def __init__(self, *args):
        super().__init__(*args)

        self.gen = 0
        self.initialized = False
        self.running = False

        # c pointer type
        p = c_void_p

        # clib setup        
        self.hashlife = cdll.LoadLibrary('hashlife.so')

        self.hashlife.init.argtypes = [c_int, c_int]
        self.hashlife.init.restype = p

        self.hashlife.start.argtypes = [p, p]
        self.hashlife.start.restype = p

        self.hashlife.get_root.argtypes = [p]
        self.hashlife.get_root.restype = p

        self.hashlife.get_cell.argtypes = [p, c_long, c_long]
        self.hashlife.get_cell.restype = c_bool

        self.hashlife.set_cell.argtypes = [p, p, c_long, c_long, c_bool]
        self.hashlife.set_cell.restype = p

        self.hashlife.run.argtypes = [p, p, c_long]
        self.hashlife.run.restype = p

        self.hashlife.end.argtypes = [p]
        self.hashlife.end.restype = None
        
        self.hashlife.clear_pixels.argtypes = [p, c_int, c_int, c_ubyte]
        self.hashlife.clear_pixels.restype = None

        self.hashlife.set_pixels.argtypes = [p, c_int, c_int, p, c_long, c_long, c_int]
        self.hashlife.set_pixels.restype = None

        self.hashlife.node_level.argtypes = [p]
        self.hashlife.node_level.restype = c_int

        self.hashlife.node_pop.argtypes = [p]
        self.hashlife.node_pop.restype = c_long

        self.hashlife.hashtable_count.argtypes = [p]
        self.hashlife.hashtable_count.restype = c_int

        # library parameters
        self.hashtable = None
        self.root = None

        # world parameters
        self.ss = 6
        self.level = 0

        # img setup
        self.pixels = np.full(self.w * self.h * 3, 127, dtype=np.ubyte)
        self.pixels_p = np.ctypeslib.as_ctypes(self.pixels)
        self.img = pyglet.image.ImageData(self.w, self.h, 'RGB', self.pixels_p)

    def __del__(self):
        print('Cleaning up...')
        self.lib_end()

    # library functions
    def lib_init(self):
        if not self.initialized:
            self.hashtable = self.hashlife.init(*self.get_valobj('rule').get_flags())
            self.initialized = True
            self.root = self.hashlife.get_root(self.hashtable)
            self.lib_set_cell(0, 0, True)
            self.lib_set_cell(0, 1, True)
            self.lib_set_cell(0, 2, True)
            self.lib_set_cell(-1, 1, True)
            self.lib_set_cell(1, 2, True)
            self.level = self.hashlife.node_level(self.root)
            self.set_val('level', self.level)
            self.set_val('states', self.hashlife.hashtable_count(self.hashtable))
            self.set_val('pop', self.hashlife.node_pop(self.root))
            self.lib_set_pixels()

    def lib_start(self):
        if self.initialized and not self.running:
            self.hashtable = self.hashlife.start(self.hashtable, self.root)
            self.level = self.hashlife.node_level(self.root)
            self.running = True

    def lib_run(self, n):
        if self.initialized and self.running:
            self.root = self.hashlife.run(self.hashtable, self.root, n)

    def lib_get_cell(self, x, y):
        if self.initialized:
            return self.hashlife.get_cell(self.root, x, y)

    def lib_set_cell(self, x, y, state):
        if self.initialized and not self.running:
            self.root = self.hashlife.set_cell(self.hashtable, self.root, x, y, state)
            self.lib_set_pixels()

    def lib_clear_pixels(self, color):
        self.hashlife.clear_pixels(self.pixels_p, self.w, self.h, color)
        self.img.set_data('RGB', self.img.width * 3, self.pixels_p)

    def lib_set_pixels(self):
        if self.initialized:
            self.hashlife.set_pixels(self.pixels_p, self.w, self.h, self.root,
                                     self.get_val('cx'), self.get_val('cy'), self.ss)
            self.img.set_data('RGB', self.img.width * 3, self.pixels_p)

    def lib_end(self):
        if self.running:
            self.hashlife.end(self.hashtable)
            self.lib_clear_pixels(127)
            self.gen = 0
            self.set_val('level', 0)
            self.set_val('states', 0)
            self.set_val('pop', 0)
            self.running = False
            self.initialized = False

    def draw(self):
        self.img.blit(self.x, self.y)

    def tick(self, dt):
        n = self.get_val('gens')
        start = time.time()
        self.lib_run(n)
        end = time.time()
        self.level = self.hashlife.node_level(self.root)
        self.gen += n

        self.set_val('ticktime', (end - start) * 1000)
        if dt:
            self.set_val('runspeed', 1 / dt)
        else:
            self.set_val('runspeed', 0)
        self.set_val('level', self.level)
        self.set_val('states', self.hashlife.hashtable_count(self.hashtable))
        self.set_val('pop', self.hashlife.node_pop(self.root))

        self.lib_set_pixels()

    def key_down(self, symbol, modifiers):
        if symbol == key.LEFT:
            self.set_val('cx', self.get_val('cx') - 4)
        elif symbol == key.RIGHT:
            self.set_val('cx', self.get_val('cx') + 4)
        elif symbol == key.UP:
            self.set_val('cy', self.get_val('cy') + 4)
        elif symbol == key.DOWN:
            self.set_val('cy', self.get_val('cy') - 4)
        elif symbol == key.J:
            self.set_val('cx', self.get_val('cx') - 16)
        elif symbol == key.L:
            self.set_val('cx', self.get_val('cx') + 16)
        elif symbol == key.I:
            self.set_val('cy', self.get_val('cy') + 16)
        elif symbol == key.K:
            self.set_val('cy', self.get_val('cy') - 16)
        elif symbol == key.A:
            if self.ss > 2:
                self.ss -= 2
        elif symbol == key.S:
            self.ss += 2
        elif symbol == key.T:
            self.tick(0)

        self.lib_set_pixels()

    def mouse_down(self, x, y, button, modifier):
        mx = self.get_val('cx') + (x - self.w // 2 + self.ss // 2) // self.ss
        my = self.get_val('cy') + (y - self.h // 2 + self.ss // 2) // self.ss
        state = self.lib_get_cell(mx, my)
        self.lib_set_cell(mx, my, not state)

    def resize(self, width, height):
        self.set_size(width - 200, height)

        del self.pixels, self.pixels_p, self.img

        self.pixels = np.full(self.w * self.h * 3, 127, dtype=np.ubyte)
        self.pixels_p = np.ctypeslib.as_ctypes(self.pixels)
        self.img = pyglet.image.ImageData(self.w, self.h, 'RGB', self.pixels_p)
        if self.root:
            self.lib_set_pixels()


class GOLWindow(pyg.window.Window):
    def set_vars(self):
        self.add_screen('1', GOLScreen(self, 200, 0, 600, 600))

        self.add_generic_valobj('rule', RuleValue('B3/S23'))
        self.add_generic_field('rule', RuleField, 5, 470, 190, 15, 'Rule', self.get_valobj('rule'))

        self.add_int_value('cx')
        self.add_int_value('cy')
        self.add_label('cx', 5, 200, color=(255, 0, 255))
        self.add_label('cy', 5, 180, color=(255, 0, 255))
        self.add_int_value('ncx')
        self.add_int_value('ncy')
        self.add_int_field('cx', 5, 240, 190, 15, 'CX', self.get_valobj('ncx'))
        self.add_int_field('cy', 5, 220, 190, 15, 'CY', self.get_valobj('ncy'))
        self.add_button('moveto', 80, 270, 40, 25, 'Move', self.moveto, visible=False)

        self.add_label('genlabel', 5, 130, color=(255, 0, 255))
        self.add_int_value('level')
        self.add_label('level', 5, 115, color=(255, 0, 255))
        self.add_int_value('pop')
        self.add_label('pop', 5, 100, color=(255, 0, 255))
        self.add_int_value('states')
        self.add_label('states', 5, 85, color=(255, 0, 255))
        self.add_float_value('ticktime', 1)
        self.add_label('ticktime', 5, 45, color=(255, 0, 255))
        self.add_float_value('runspeed', 1)
        self.add_label('runspeed', 5, 30, color=(255, 0, 255))

        self.ticking = False
        self.add_button('init', 5, 440, 100, 25, 'Initialize', self.initialize)
        self.add_button('start', 5, 400, 40, 25, 'Start', self.start, visible=False)
        self.add_button('end', 5, 400, 40, 25, 'End', self.end, visible=False)
        self.add_button('tick', 55, 400, 40, 25, 'Tick(t)', self.tick_once, visible=False)
        self.add_button('run', 105, 400, 40, 25, 'Run', self.run, visible=False)
        self.add_button('stop', 105, 400, 40, 25, 'Stop', self.stop, visible=False)

        self.add_int_value('gens', 1, limit='l', low=1)
        self.add_int_field('gens', 5, 340, 190, 15, 'Gen speed (gen/tick)', self.get_valobj('gens'))
        self.add_int_value('speed', 10, limit='l', low=1)
        self.add_int_field('speed', 5, 320, 190, 15, 'Tick speed (tick/s)', self.get_valobj('speed'))

        self.add_button('help', 80, 500, 40, 25, 'Help', self.help)

    def update_labels(self):
        self.labels['cx'].set_text('Current CX: %d' % self.get_val('cx'))
        self.labels['cy'].set_text('Current CY: %d' % self.get_val('cy'))

        self.labels['genlabel'].set_text('Generation %d' % self.screens['1'].gen)
        self.labels['level'].set_text('World size: 2^%d' % self.get_val('level'))
        self.labels['pop'].set_text('Population: %d' % self.get_val('pop'))
        self.labels['states'].set_text('Stored states: %d' % self.get_val('states'))

        self.labels['ticktime'].set_text(' Ticktime: %s ms' % str(round(self.get_val('ticktime'), 2)))
        self.labels['runspeed'].set_text('Run speed: %s gen/s' % str(round(self.get_val('runspeed'), 2)))

    def initialize(self):
        self.screens['1'].lib_init()
        self.buttons['init'].off()
        self.buttons['start'].on()
        self.buttons['moveto'].on()

    def start(self):
        self.screens['1'].lib_start()
        self.buttons['start'].off()
        self.buttons['end'].on()
        self.buttons['tick'].on()
        self.buttons['run'].on()

    def end(self):
        self.stop()
        self.screens['1'].lib_end()
        self.buttons['init'].on()
        self.buttons['start'].off()
        self.buttons['end'].off()
        self.buttons['tick'].off()
        self.buttons['run'].off()
        self.buttons['moveto'].off()

    def tick_once(self):
        self.screens['1'].tick(0)

    def run(self):
        if not self.ticking:
            self.ticking = True
            clock.schedule_interval(self.tick, 1 / self.get_val('speed'))
            self.buttons['tick'].off()
            self.buttons['run'].off()
            self.buttons['stop'].on()

    def stop(self):
        if self.ticking:
            self.ticking = False
            clock.unschedule(self.tick)
            self.buttons['tick'].on()
            self.buttons['stop'].off()
            self.buttons['run'].on()

    def moveto(self):
        self.set_val('cx', self.get_val('ncx'))
        self.set_val('cy', self.get_val('ncy'))
        self.screens['1'].lib_set_pixels()

    def help(self):
        if sys.platform.startswith('darwin'):
            subprocess.call(('open', 'readme.txt'))
        elif os.name == 'nt':
            os.startfile('readme.txt')
        elif os.name == 'posix':
            subprocess.call(('xdg-open', 'readme.txt'))

    def tick(self, dt):
        self.screens['1'].tick(dt)


pyg.run(GOLWindow, 800, 600, 'Game of Life')
