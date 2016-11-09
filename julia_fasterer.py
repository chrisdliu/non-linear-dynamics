import pyg
import pyglet
import numpy as np
from numba import jit, guvectorize
import time


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


@jit('int64(complex128, complex128, complex128, complex128, float64, int64)')
def get_color_poly(z, a, b, c, limit, max_iter):
    for n in range(max_iter):
        if np.abs(z) > limit:
            return color(n, max_iter)
        z = a * z * z + b * z + c
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


@guvectorize(['(complex128[:], complex128[:], complex128[:], complex128[:], float64[:], int32[:], int32[:])'], '(n),(),(),(),(),()->(n)', target='parallel')
def julia_poly(z, a, b, c, limit, max_iter, output):
    a = a[0]
    b = b[0]
    c = c[0]
    limit = limit[0]
    max_iter = max_iter[0]
    for i in range(z.shape[0]):
        output[i] = get_color_poly(z[i], a, b, c, limit, max_iter)


@jit
def get_data_call(mode, w, h, bl_x, bl_y, tr_x, tr_y, limit, max_iter, args):
    zr = np.linspace(bl_x, tr_x, w, dtype=np.float64)
    zi = np.linspace(bl_y, tr_y, h, dtype=np.float64)
    z = zr + zi[:, None] * 1j  # [y, bottom to top][x, left to right]
    if mode == 0:
        color_data = julia_z2_guvec(z, args[0], limit, max_iter)
    elif mode == 1:
        color_data = mandel_guvec(z, limit, max_iter)
    elif mode == 2:
        color_data = julia_z3_guvec(z, args[0], limit, max_iter)
    elif mode == 3:
        color_data = julia_sin_guvec(z, args[0], limit, max_iter)
    else:
        print('poly')
        color_data = julia_poly(z, args[0], args[1], args[2], limit, max_iter)
    return color_data


@jit
def get_data(mode, w, h, bl_x, bl_y, tr_x, tr_y, limit, max_iter, args):
    color_data = get_data_call(mode, w, h, bl_x, bl_y, tr_x, tr_y, limit, max_iter, args)
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


@jit
def compress(p_colors, w, h):
    lines = np.empty(w * h * 6, dtype=np.int32)
    lines_idx = 0
    colors = np.empty(w * h * 6, dtype=np.int32)
    colors_idx = 0
    p_colors_idx = 0
    for y in range(h):
        color = p_colors[p_colors_idx]
        start_x = 0
        for x in range(1, w):
            p_colors_idx += 3
            if p_colors[p_colors_idx] != color:
                # lines.extend((start_x, y, 0, x - 1, y, 0))
                lines[lines_idx] = start_x
                lines[lines_idx + 1] = y
                lines[lines_idx + 2] = 0
                lines[lines_idx + 3] = x
                lines[lines_idx + 4] = y
                lines[lines_idx + 5] = 0
                lines_idx += 6
                # colors.extend((color, ) * 6)
                for i in range(6):
                    colors[colors_idx + i] = color
                colors_idx += 6
                color = p_colors[p_colors_idx]
                start_x = x
        # lines.extend((start_x, y, 0, w - 1, y, 0))
        lines[lines_idx] = start_x
        lines[lines_idx + 1] = y
        lines[lines_idx + 2] = 0
        lines[lines_idx + 3] = w
        lines[lines_idx + 4] = y
        lines[lines_idx + 5] = 0
        lines_idx += 6
        # colors.extend((color, ) * 6)
        for i in range(6):
            colors[colors_idx + i] = color
        colors_idx += 6
        p_colors_idx += 3
    cmpr = 100 - (((lines_idx // 6) / (len(p_colors) // 3)) * 100)
    return lines[:lines_idx], colors[:colors_idx], cmpr


class JuliaScreen(pyg.screen.GraphScreen):
    def __init__(self, x, y, width, height, bg=(255, 255, 255), valset=None):
        self.mode = 0
        self.points = []
        super().__init__(x, y, width, height, bg=bg, valset=valset)

    def reset_graph(self):
        self.sx = 0
        self.sy = 0
        self.sw = 5 * (self.w / 500)
        self.sh = 5 * (self.h / 500)

    def set_mode(self, mode):
        self.mode = mode
        self.render()

    def set_graph_points(self):
        bl_x, bl_y = self.on_plot(0, 0)
        tr_x, tr_y = self.on_plot(self.w, self.h)
        a = self.get_val('a')
        b = self.get_val('b')
        c = self.get_val('c')
        max_iter = self.get_val('max_iter')
        limit = self.get_val('limit')

        if self.mode in [0, 2, 3]:
            args = [c, ]
        elif self.mode == 4:
            args = [a, b, c]
        else:
            args = []
        colors = get_data(self.mode, self.w, self.h, bl_x, bl_y, tr_x, tr_y, limit, max_iter, args)
        lines, colors, cmpr = compress(colors, self.w, self.h)
        self.valset.set_val('cmpr', cmpr)

        # self.set_points_both(points, colors)
        self.set_lines_both(lines, colors)

    def render(self):
        start = time.clock()
        self.set_graph_points()
        end = time.clock()
        self.valset.set_val('calctime', ((end - start) * 1000))
        start = time.clock()
        self.flush()
        end = time.clock()
        self.valset.set_val('flushtime', ((end - start) * 1000))

    def key_down(self, symbol, modifiers):
        super().key_down(symbol, modifiers)

    def resize(self, width, height):
        self.refit(width, height - 200)

    def mouse_move(self, x, y, dx, dy):
        if self.is_inside(x + self.x, y + self.y):
            cx, cy = self.on_plot(x, y)
            self.set_val('c', cx + cy * 1j)
            self.render()


class JuliaWindow(pyg.window.Window):
    def set_vars(self):
        self.valset.add_value('sz', .5)
        self.valset.add_value('max_iter', 25)
        self.valset.add_value('limit', 2.0)
        self.valset.add_value('a', 0)
        self.valset.add_value('b', 0)
        self.valset.add_value('c', -.77 + .22j)
        self.valset.add_value('cmpr', 0.0)
        self.valset.add_value('calctime', 0.0)
        self.valset.add_value('flushtime', 0.0)

        main = JuliaScreen(0, 200, 500, 500, valset=self.valset)
        self.add_screen('main', main)

        self.add_float_field('zoomfield', 230, 55, 100, 15, 'Zoom', self.valset.get_obj('sz'), limit='ul', inclusive='', low=0, high=1)
        self.add_int_field('max_iter', 230, 155, 100, 15, 'Max Iter', self.valset.get_obj('max_iter'), limit='l', low=1)
        self.add_float_field('limit', 230, 135, 100, 15, 'Limit', self.valset.get_obj('limit'), limit='l', inclusive='', low=0)
        self.add_complex_field('a', 230, 115, 100, 15, 'A', self.valset.get_obj('a'))
        self.add_complex_field('b', 230, 95, 100, 15, 'B', self.valset.get_obj('b'))
        self.add_complex_field('c', 230, 75, 100, 15, 'C', self.valset.get_obj('c'))

        self.add_button('resetb', 150, 120, 40, 40, 'Reset', self.screens['main'].reset)
        self.add_button('m1b', 50, 130, 80, 20, 'Julia z^2+c', lambda: self.screens['main'].set_mode(0))
        self.add_button('m2b', 50, 100, 80, 20, 'Mandelbrot', lambda: self.screens['main'].set_mode(1))
        self.add_button('m3b', 50, 70, 80, 20, 'Julia z^3+c', lambda: self.screens['main'].set_mode(2))
        self.add_button('m4b', 50, 40, 80, 20, 'Julia c*sin(z)', lambda: self.screens['main'].set_mode(3))
        self.add_button('m5b', 50, 10, 80, 20, 'Julia poly', lambda: self.screens['main'].set_mode(4))

        self.add_label('leftlabel', 10, 180, '%.5f' % (self.screens['main'].sx - self.screens['main'].sw / 2), color=(255, 0, 255))
        self.add_label('rightlabel', self.screens['main'].w - 60, 180, '%.5f' % (self.screens['main'].sx + self.screens['main'].sw / 2), color=(255, 0, 255))
        self.add_label('toplabel', 10, self.screens['main'].h + 180, '%.5f' % (self.screens['main'].sy + self.screens['main'].sh / 2), color=(255, 0, 255))
        self.add_label('bottomlabel', 10, 210, '%.5f' % (self.screens['main'].sy - self.screens['main'].sh / 2), color=(255, 0, 255))
        self.add_label('cmprlabel', self.screens['main'].w - 160, 130, 'compression: %.5f' % self.valset.get_val('cmpr'))
        self.add_label('calclabel', self.screens['main'].w - 160, 110, '  calc time: %.5f' % self.valset.get_val('calctime'))
        self.add_label('flushlabel', self.screens['main'].w - 160, 90, ' flush time: %.5f' % self.valset.get_val('flushtime'))

    def render(self):
        for screen in self.screens.values():
            screen.render()
        for button in self.buttons.values():
            button.render()
        for field in self.fields.values():
            field.render()

    def update_labels(self):
        self.labels['leftlabel'].set_text('%.5f' % (self.screens['main'].sx - self.screens['main'].sw / 2))
        self.labels['rightlabel'].set_text('%.5f' % (self.screens['main'].sx + self.screens['main'].sw / 2))
        self.labels['rightlabel'].set_pos(self.screens['main'].w - 60, 180)
        self.labels['toplabel'].set_text('%.5f' % (self.screens['main'].sy + self.screens['main'].sh / 2))
        self.labels['toplabel'].set_pos(10, self.screens['main'].h + 180)
        self.labels['bottomlabel'].set_text('%.5f' % (self.screens['main'].sy - self.screens['main'].sh / 2))
        self.labels['cmprlabel'].set_text('compression: %.5f %%' % self.valset.get_val('cmpr'))
        self.labels['cmprlabel'].set_pos(self.screens['main'].w - 160, 130)
        self.labels['calclabel'].set_text('  calc time: %.5f ms' % self.valset.get_val('calctime'))
        self.labels['calclabel'].set_pos(self.screens['main'].w - 160, 110)
        self.labels['flushlabel'].set_text(' flush time: %.5f ms' % self.valset.get_val('flushtime'))
        self.labels['flushlabel'].set_pos(self.screens['main'].w - 160, 90)


window = JuliaWindow(width=500, height=700, caption='Julia Graph', bg=(0, 0, 0, 1), resizable=True)
pyglet.app.run()
