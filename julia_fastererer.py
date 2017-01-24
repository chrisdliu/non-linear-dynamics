import pyg
import pyglet
import numpy as np
from numba import jit, guvectorize
import time
import ctypes


@jit
def get_pos(x, y, w):
    return (y * w + x) * 3


@jit('int32(int32, int32)')
def color(iter, max_iter):
    return int((iter / (max_iter + 1)) * 255)


@jit('int64(complex128, complex128, float64, int64)')
def get_color_z2(z, c, limit, max_iter):
    limit2 = limit * limit
    zr = z.real
    zi = z.imag
    cr = c.real
    ci = c.imag
    for n in range(max_iter):
        zr2 = zr * zr
        zi2 = zi * zi
        if zr2 + zi2 > limit2:
            return color(n, max_iter)
        zi = 2 * zr * zi + ci
        zr = zr2 - zi2 + cr
    return 255


@jit('int64(complex128, complex128, float64, int64)')
def get_color_z3(z, c, limit, max_iter):
    for n in range(max_iter):
        if np.abs(z) > limit:
            return color(n, max_iter)
        z = z * z * z + c
    return 255


@jit('int64(complex128, complex128, float64, int64)')
def get_color_sin(z, c, limit, max_iter):
    for n in range(max_iter):
        if np.abs(z) > limit:
            return color(n, max_iter)
        z = c * np.sin(z)
    return 255


@guvectorize(['(complex128[:], float64[:], int32[:], int32[:])'], '(n),(),()->(n)', target='parallel')
def mandel_guvec(z, limit, max_iter, output):
    limit = limit[0]
    max_iter = max_iter[0]
    for i in range(z.shape[0]):
        output[i] = get_color_z2(z[i], z[i], limit, max_iter)


@guvectorize(['(complex128[:], complex128[:], float64[:], int32[:], int32[:])'], '(n),(),(),()->(n)', target='parallel')
def julia_z2_guvec(z, c, limit, max_iter, output):
    c = c[0]
    limit = limit[0]
    max_iter = max_iter[0]
    for i in range(z.shape[0]):
        output[i] = get_color_z2(z[i], c, limit, max_iter)


@guvectorize(['(complex128[:], complex128[:], float64[:], int32[:], int32[:])'], '(n),(),(),()->(n)', target='parallel')
def julia_z3_guvec(z, c, limit, max_iter, output):
    c = c[0]
    limit = limit[0]
    max_iter = max_iter[0]
    for i in range(z.shape[0]):
        output[i] = get_color_z3(z[i], c, limit, max_iter)


@guvectorize(['(complex128[:], complex128[:], float64[:], int32[:], int32[:])'], '(n),(),(),()->(n)', target='parallel')
def julia_sin_guvec(z, c, limit, max_iter, output):
    c = c[0]
    limit = limit[0]
    max_iter = max_iter[0]
    for i in range(z.shape[0]):
        output[i] = get_color_sin(z[i], c, limit, max_iter)


@jit
def get_data_call(mode, w, h, bl_x, bl_y, tr_x, tr_y, limit, max_iter, c):
    zr = np.linspace(bl_x, tr_x, w, dtype=np.float64)
    zi = np.linspace(bl_y, tr_y, h, dtype=np.float64)
    z = zr + zi[:, None] * 1j  # [y, bottom to top][x, left to right]
    if mode == 0:
        color_data = julia_z2_guvec(z, c, limit, max_iter)
    elif mode == 1:
        color_data = mandel_guvec(z, limit, max_iter)
    elif mode == 2:
        color_data = julia_z3_guvec(z, c, limit, max_iter)
    else:
        color_data = julia_sin_guvec(z, c, limit, max_iter)
    return color_data


@jit
def get_data(mode, w, h, bl_x, bl_y, tr_x, tr_y, limit, max_iter, c):
    color_data = get_data_call(mode, w, h, bl_x, bl_y, tr_x, tr_y, limit, max_iter, c)
    idx_max = w * h * 3
    colors = np.zeros(idx_max, dtype=np.int16)
    for y in range(h):
        for x in range(w):
            idx = get_pos(x, y, w)
            color = color_data[y][x]
            colors[idx] = color
            colors[idx + 1] = color
            colors[idx + 2] = color
    return colors


class JuliaScreen(pyg.screen.GraphScreen):
    def __init__(self, x, y, width, height, valset, zoom_valobj, bg=(255, 255, 255), visible=True):
        self.mode = 0
        self.mouse_c = False
        super().__init__(x, y, width, height, 0, 0, 5, 5, valset, zoom_valobj, bg=bg, visible=visible)
        # img
        rawdata = np.zeros(self.w * self.h * 3, dtype=np.ubyte)
        self.img = pyglet.image.ImageData(self.w, self.h, 'RGB', rawdata)

    def set_mode(self, mode):
        self.mode = mode

    def toggle_mouse_c(self):
        self.mouse_c = not self.mouse_c

    def set_graph_points(self):
        #calc
        start = time.time()
        bl_x, bl_y = self.on_plot(0, 0)
        tr_x, tr_y = self.on_plot(self.w, self.h)
        c = self.get_val('c')
        max_iter = self.get_val('max_iter')
        limit = self.get_val('limit')
        colors = get_data(self.mode, self.w, self.h, bl_x, bl_y, tr_x, tr_y, limit, max_iter, c)
        end = time.time()
        self.valset.set_val('calctime', ((end - start) * 1000))

        #flush
        start = time.time()
        del self.img
        rawdata = colors.astype(np.ubyte).ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte))
        self.img = pyglet.image.ImageData(self.w, self.h, 'RGB', rawdata)
        end = time.time()
        self.valset.set_val('flushtime', ((end - start) * 1000))

    def render(self):
        start = time.time()
        self.set_graph_points()
        end = time.time()
        self.valset.set_val('calctime', ((end - start) * 1000))
        start = time.time()
        self.flush()
        end = time.time()
        self.valset.set_val('flushtime', ((end - start) * 1000))

    def draw(self):
        super().draw()
        self.img.blit(self.x, self.y)

    def key_down(self, symbol, modifiers):
        super().key_down(symbol, modifiers)

    def resize(self, width, height):
        self.refit(width, height - 200)

    def mouse_move(self, x, y, dx, dy):
        if self.is_inside(x + self.x, y + self.y) and self.mouse_c:
            cx, cy = self.on_plot(x, y)
            self.set_val('c', cx + cy * 1j)


class JuliaWindow(pyg._window.Window):
    def set_vars(self):
        self.valset.add_float_value('sz', .5, limit='ul', inclusive='', low=0, high=1)
        self.valset.add_int_value('max_iter', 25, limit='l', low=1)
        self.valset.add_float_value('limit', 2.0, limit='l', inclusive='', low=0)
        self.valset.add_complex_value('c', -.77 + .22j)
        self.valset.add_float_value('calctime', 0.0)
        self.valset.add_float_value('flushtime', 0.0)

        main = JuliaScreen(0, 200, 500, 500, self.valset, self.valset.get_valobj('sz'))
        self.add_screen('main', main)

        self.add_float_field('zoomfield', 230, 55, 100, 15, 'Zoom', self.valset.get_valobj('sz'))
        self.add_int_field('max_iter', 230, 155, 100, 15, 'Max Iter', self.valset.get_valobj('max_iter'))
        self.add_float_field('limit', 230, 135, 100, 15, 'Limit', self.valset.get_valobj('limit'))
        self.add_complex_field('c', 230, 75, 100, 15, 'C', self.valset.get_valobj('c'))

        self.add_button('resetb', 150, 120, 40, 40, 'Reset', self.reset)
        self.add_button('mouse_c', 150, 60, 40, 40, 'Mouse C', self.toggle_mouse_c)
        self.add_button('m1b', 50, 130, 80, 20, 'Julia z^2+c', lambda: self.set_mode(0))
        self.add_button('m2b', 50, 100, 80, 20, 'Mandelbrot', lambda: self.set_mode(1))
        self.add_button('m3b', 50, 70, 80, 20, 'Julia z^3+c', lambda: self.set_mode(2))
        self.add_button('m4b', 50, 40, 80, 20, 'Julia c*sin(z)', lambda: self.set_mode(3))

        main = self.get_screen('main')
        self.add_label('leftlabel', 10, 180, '%.5f' % main.min_gx, color=(255, 0, 255))
        self.add_label('rightlabel', self.width - 60, 180, '%.5f' % main.max_gx, color=(255, 0, 255))
        self.add_label('toplabel', 10, self.height + 180, '%.5f' % main.max_gy, color=(255, 0, 255))
        self.add_label('bottomlabel', 10, 210, '%.5f' % main.min_gy, color=(255, 0, 255))
        self.add_label('calclabel', self.width - 160, 110, '  calc time: %.5f' % self.valset.get_val('calctime'))
        self.add_label('flushlabel', self.width - 160, 90, ' flush time: %.5f' % self.valset.get_val('flushtime'))

    def toggle_mouse_c(self):
        self.screens['main'].toggle_mouse_c()

    def reset(self):
        self.screens['main'].reset_screen()

    def set_mode(self, mode):
        if mode == self.screens['main'].mode:
            return
        self.screens['main'].set_mode(mode)
        self.render()

    def update_labels(self):
        main = self.get_screen('main')
        self.labels['leftlabel'].set_text('%.5f' % main.min_gx)
        self.labels['rightlabel'].set_text('%.5f' % main.max_gx)
        self.labels['rightlabel'].set_pos(self.width - 60, 180)
        self.labels['toplabel'].set_text('%.5f' % main.max_gy)
        self.labels['toplabel'].set_pos(10, self.height + 180)
        self.labels['bottomlabel'].set_text('%.5f' % main.min_gy)
        self.labels['calclabel'].set_text('  calc time: %.5f ms' % self.valset.get_val('calctime'))
        self.labels['calclabel'].set_pos(self.width - 160, 110)
        self.labels['flushlabel'].set_text(' flush time: %.5f ms' % self.valset.get_val('flushtime'))
        self.labels['flushlabel'].set_pos(self.width - 160, 90)

    def mouse_move(self, x, y, dx, dy):
        super().mouse_move(x, y, dx, dy)
        if self.screens['main'].mouse_c:
            self.fields['c'].update_label()
            self.screens['main'].render()

    def on_resize(self, width, height):
        super().on_resize(width, height)


window = JuliaWindow(width=500, height=700, caption='Julia Graph', bg=(0, 0, 0, 1), resizable=True)
pyglet.app.run()
