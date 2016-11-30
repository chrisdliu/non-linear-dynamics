"""
By Chris Liu

Requires pyglet, numpy, numba, and pyg to run

How to use:
Left click to zoom in
Right click to zoom out
Arrow keys to move screen
Click to use buttons
Click to select fields, type to enter characters, enter to parse input
Click and hold to move sliders
Keys
r: resets screen
c: toggles mouse c
j: previous saved coords
k: next saved coords
s: save current coords
g: goto selected coords
y: delete selected coords

Note: split screen is really slow because of some stupid bug
"""


import pyg
import pyglet
import numpy as np
from numba import jit, vectorize, guvectorize
import time
import ctypes



@jit
def f(z):
    #return z ** 4 - 1
    return (z ** 2 + 1) * (z ** 2 - 5.29)


@jit
def fprime(z):
    return 4 * (z ** 3 - 2.145 * z)

@jit
def get_root(guess, roots):
    root = roots[0]
    diff = abs(guess - root)
    for i in range(1, roots.shape[0]):
        if abs(guess - roots[i]) < diff:
            root = roots[i]
            diff = abs(guess - root)
    return root


@guvectorize('(complex128[:], complex128[:], int32[:], complex128[:])', '(),(n),()->()', target='parallel')
def newtons(guess, roots, max_iter, output):
    guess = guess[0]
    max_iter = max_iter[0]
    for i in range(max_iter):
        fp = fprime(guess)
        if fp == 0:
            output[0] = get_root(guess, roots)
            break
        guess -= f(guess) / fp
        if i == max_iter - 1:
            output[0] = get_root(guess, roots)


@guvectorize('(complex128[:], complex128[:], int32[:])', '(),(n)->()', target='parallel')
def parse_color_data(color_data, roots, output):
    color_data = color_data[0]
    if color_data == roots[0]:
        r = 255
        g = 0
        b = 0
    elif color_data == roots[1]:
        r = 255
        g = 255
        b = 0
    elif color_data == roots[2]:
        r = 0
        g = 255
        b = 0
    elif color_data == roots[3]:
        r = 0
        g = 0
        b = 255
    else:
        r = 0
        g = 0
        b = 0
    output[0] = ((r & 0xff) << 16) | ((g & 0xff) << 8) | (b & 0xff)


@jit
def vectorize_call(w, h, bl_x, bl_y, tr_x, tr_y, roots, max_iter):
    zr = np.linspace(bl_x, tr_x, w, dtype=np.float64, endpoint=False)
    zi = np.linspace(bl_y, tr_y, h, dtype=np.float64, endpoint=False)
    z = zr[:, None] + zi * 1j  # [x][y]
    color_data = newtons(z, roots, max_iter)
    return parse_color_data(color_data, roots)


@jit('int32(int32, int32, int32)')
def get_pos(x, y, w):
    return (y * w + x) * 3


@jit
def get_data(w, h, bl_x, bl_y, tr_x, tr_y, roots, max_iter):
    color_data = vectorize_call(w, h, bl_x, bl_y, tr_x, tr_y, roots, max_iter)
    idx_max = w * h * 3
    colors = np.empty(idx_max, dtype=np.ubyte)
    for y in range(h):
        for x in range(w):
            idx = get_pos(x, y, w)
            color = color_data[x][y]
            colors[idx] = (color >> 16) & 0xff
            colors[idx + 1] = (color >> 8) & 0xff
            colors[idx + 2] = color & 0xff
    return colors


class NewtonScreen(pyg.screen.GraphScreen):
    def __init__(self, x, y, width, height, valset, zoom_valobj, bg = (255, 255, 255), visible = True):
        super().__init__(x, y, width, height, 0, 0, 5, 5, valset, zoom_valobj, bg=bg, visible=visible)
        self.img = pyglet.image.ImageData(self.w, self.h, 'RGB', np.zeros(self.w * self.h * 3, dtype=np.ubyte).ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte)))
        #self.f = lambda x: x * (x - 1) * (x - 2)
        #self.fprime = lambda x: 3 * x * x - 6 * x + 2
        #self.f = lambda x: x ** 4 - 1
        #self.fprime = lambda x: 4 * x ** 3
        self.roots = np.array([1j, -1j, 2.3, -2.3], dtype=np.complex128)
        '''
        self.palette = {
            self.roots[0]: [255, 0, 0],
            self.roots[1]: [255, 255, 0],
            self.roots[2]: [0, 255, 0],
            self.roots[3]: [0, 0, 255],
        }
        '''

    def render(self):
        """
        Renders the screen and creates an image with the pixel data
        """
        #calc
        start = time.time()
        bl_x, bl_y = self.on_plot(0, 0)
        tr_x, tr_y = self.on_plot(self.w, self.h)
        max_iter = self.get_val('max_iter')
        colors = get_data(self.w, self.h, bl_x, bl_y, tr_x, tr_y, self.roots, max_iter)
        end = time.time()
        self.valset.set_val('calctime', ((end - start) * 1000))

        #flush
        start = time.time()
        del self.img
        rawdata = colors.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte))
        self.img = pyglet.image.ImageData(self.w, self.h, 'RGB', rawdata)
        end = time.time()
        self.valset.set_val('flushtime', ((end - start) * 1000))

    def draw(self):
        """
        Draws the image created in render()
        """
        #super().draw()
        self.img.blit(self.x, self.y)

    def resize(self, width, height):
        self.refit(width, height - 200)


class NewtonWindow(pyg.window.Window):
    def set_vars(self):
        """
        Adds the gui components
        """
        self.valset.add_float_value('gz', .5, limit='ul', inclusive='', low=0, high=1)
        self.add_float_field('zoomfield', 150, 120, 120, 15, 'Zoom Ratio', self.get_valobj('gz'))
        self.valset.add_float_value('calctime', 0.0)
        self.valset.add_float_value('flushtime', 0.0)
        self.valset.add_int_value('max_iter', 50, limit='l', low=1)

        main = NewtonScreen(0, 200, 500, 500, self.valset, self.get_valobj('gz'))
        self.add_screen('main', main)

        self.add_button('resetb', 10, 10, 40, 15, 'Reset(r)', self.reset)

        self.add_int_field('max_iter', 150, 80, 120, 15, 'Max Iter', self.get_valobj('max_iter'))

        self.add_label('leftlabel', 10, 180, '%.5f' % self.get_screen('main').min_gx, color=(255, 0, 255))
        self.add_label('rightlabel', self.width - 60, 180, '%.5f' % self.get_screen('main').max_gx, color=(255, 0, 255))
        self.add_label('toplabel', 10, self.height - 20, '%.5f' % self.get_screen('main').max_gy, color=(255, 0, 255))
        self.add_label('bottomlabel', 10, 210, '%.5f' % self.get_screen('main').min_gy, color=(255, 0, 255))
        self.add_label('zoomlabel', self.width * 3 // 5, 180, 'Zoom: %.5E' % self.get_screen('main').total_zoom)

        self.add_label('calclabel', self.width - 140, 170, '  calc time: %.3f' % self.valset.get_val('calctime'), color=(0, 240, 120))
        self.add_label('flushlabel', self.width - 140, 155, ' flush time: %.3f' % self.valset.get_val('flushtime'), color=(0, 240, 120))

    def reset(self):
        self.screens['main'].reset()

    def update_labels(self):
        self.labels['leftlabel'].set_text('%.5f' % self.get_screen('main').min_gx)
        self.labels['rightlabel'].set_text('%.5f' % self.get_screen('main').max_gx)
        self.labels['rightlabel'].set_pos(self.width - 60, 180)
        self.labels['toplabel'].set_text('%.5f' % self.get_screen('main').max_gy)
        self.labels['toplabel'].set_pos(10, self.height - 20)
        self.labels['bottomlabel'].set_text('%.5f' % self.get_screen('main').min_gy)
        self.get_label('zoomlabel').set_pos(self.width * 3 // 5, 180)
        self.get_label('zoomlabel').set_text('Zoom: %.5E' % self.get_screen('main').total_zoom)


window = NewtonWindow(width=500, height=700, caption='Julia Graph', bg=(0, 0, 0, 1), resizable=True)
pyglet.app.run()
