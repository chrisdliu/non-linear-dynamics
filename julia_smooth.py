import pyg
import pyglet
import numpy as np
from numba import jit, vectorize, guvectorize
import time
import ctypes


@jit
def get_pos(x, y, w):
    return (y * w + x) * 3


@jit('int32(int32, int32)')
def color(iter, max_iter):
    return int((iter / (max_iter + 1)) * 255)


@jit('float64(int32, float64, float64)')
def norm_z2(iter, zr2, zi2):
    return iter + 1 - np.log2(np.log2(np.power(zr2 + zi2, .5)))


@jit('float64(complex128, complex128, float64, int32)')
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
            return norm_z2(n, zr2, zi2) # -0.62,0.54
        zi = 2 * zr * zi + ci
        zr = zr2 - zi2 + cr
    return 0


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


palette_colors = np.array([[0, 0, 0], [100, 0, 100], [255, 255, 255], [255, 161, 3]]) #[255, 161, 3]])
palette = np.array([[0, 0, 0]])


@jit
def set_palette(max_iter):
    pal_col_len = len(palette_colors)
    max_iter -= max_iter % pal_col_len + pal_col_len
    step = max_iter // 4
    palette = np.empty((max_iter, 3), dtype=np.int32)
    for i in range(pal_col_len):
        c1 = palette_colors[i]
        if i == pal_col_len - 1:
            c2 = palette_colors[0]
        else:
            c2 = palette_colors[i + 1]
        r = np.linspace(c1[0], c2[0], step, False)
        g = np.linspace(c1[1], c2[1], step, False)
        b = np.linspace(c1[2], c2[2], step, False)
        p = np.stack((r, g, b), axis=-1)
        palette[i*step:(i+1)*step] = p
    return palette


@guvectorize('(complex128[:], float64[:], int32[:], int32[:,:], int32[:])', '(n),(),(),(p,q)->(n)', target='parallel')
def mandel_guvec(z, limit, max_iter, palette, output):
    limit = limit[0]
    max_iter = max_iter[0]
    for i in range(z.shape[0]):
        norm = get_color_z2(z[i], z[i], limit, max_iter)
        intnorm = int(norm)
        c1 = palette[intnorm % len(palette)]
        c2 = palette[(intnorm + 1) % len(palette)]
        t = norm % 1
        r = int(c1[0] + (c2[0] - c1[0]) * t)
        g = int(c1[1] + (c2[1] - c1[1]) * t)
        b = int(c1[2] + (c2[2] - c1[2]) * t)
        output[i] = ((r & 0xff) << 16) | ((g & 0xff) << 8) | (b & 0xff)


@guvectorize(['(complex128[:], complex128[:], float64[:], int32[:], int32[:,:], int32[:])'], '(n),(),(),(),(p,q)->(n)', target='parallel')
def julia_z2_guvec(z, c, limit, max_iter, palette, output):
    c = c[0]
    limit = limit[0]
    max_iter = max_iter[0]
    for i in range(z.shape[0]):
        norm = get_color_z2(z[i], c, limit, max_iter)
        intnorm = int(norm)
        c1 = palette[intnorm % len(palette)]
        c2 = palette[(intnorm + 1) % len(palette)]
        t = norm % 1
        r = int(c1[0] + (c2[0] - c1[0]) * t)
        g = int(c1[1] + (c2[1] - c1[1]) * t)
        b = int(c1[2] + (c2[2] - c1[2]) * t)
        output[i] = ((r & 0xff) << 16) | ((g & 0xff) << 8) | (b & 0xff)


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
def get_data_call(mode, w, h, bl_x, bl_y, tr_x, tr_y, limit, max_iter, c, palette):
    zr = np.linspace(bl_x, tr_x, w, dtype=np.float64)
    zi = np.linspace(bl_y, tr_y, h, dtype=np.float64)
    z = zr + zi[:, None] * 1j  # [y, bottom to top][x, left to right]
    if mode == 0:
        color_data = julia_z2_guvec(z, c, limit, max_iter, palette)
    elif mode == 1:
        color_data = mandel_guvec(z, limit, max_iter, palette)
    elif mode == 2:
        color_data = julia_z3_guvec(z, c, limit, max_iter)
    else:
        color_data = julia_sin_guvec(z, c, limit, max_iter)
    return color_data


@jit
def get_data(mode, w, h, bl_x, bl_y, tr_x, tr_y, limit, max_iter, c, palette):
    color_data = get_data_call(mode, w, h, bl_x, bl_y, tr_x, tr_y, limit, max_iter, c, palette)
    idx_max = w * h * 3
    colors = np.zeros(idx_max, dtype=np.int16)
    for y in range(h):
        for x in range(w):
            idx = get_pos(x, y, w)
            color = color_data[y][x]
            colors[idx] = (color >> 16) & 0xff
            colors[idx + 1] = (color >> 8) & 0xff
            colors[idx + 2] = color & 0xff
    return colors


class JuliaScreen(pyg.screen.GraphScreen):
    def __init__(self, x, y, width, height, bg=(255, 255, 255), valset=None, visible=True):
        self.mode = 1
        self.mouse_c = False
        super().__init__(x, y, width, height, 0, 0, 5, 5, bg=bg, valset=valset, visible=visible)
        rawdata = np.zeros(self.w * self.h * 3, dtype=np.ubyte)
        self.img = pyglet.image.ImageData(self.w, self.h, 'RGB', rawdata)

    def reset_graph(self):
        self.sx = 0
        self.sy = 0
        self.sw = 5 * (self.w / 500)
        self.sh = 5 * (self.h / 500)

    def set_mode(self, mode):
        self.mode = mode

    def toggle_mouse_c(self):
        self.mouse_c = not self.mouse_c

    def render(self):
        #calc
        start = time.clock()
        bl_x, bl_y = self.on_plot(0, 0)
        tr_x, tr_y = self.on_plot(self.w, self.h)
        c = self.get_val('c')
        max_iter = self.get_val('max_iter')
        global palette
        if len(palette) != max_iter:
            palette = set_palette(max_iter)
        limit = self.get_val('limit')
        colors = get_data(self.mode, self.w, self.h, bl_x, bl_y, tr_x, tr_y, limit, max_iter, c, palette)
        end = time.clock()
        self.valset.set_val('calctime', ((end - start) * 1000))

        #flush
        start = time.clock()
        c_ubyte_p = ctypes.POINTER(ctypes.c_ubyte)
        colors_ubyte = colors.astype(np.ubyte)
        rawdata = colors_ubyte.ctypes.data_as(c_ubyte_p)
        self.img.set_data('RGB', self.img.width * 3, rawdata)
        end = time.clock()
        self.valset.set_val('flushtime', ((end - start) * 1000))

    def on_draw(self):
        super().on_draw()
        self.img.blit(self.x, self.y)

    def resize(self, width, height):
        self.refit(width, height - 200)
        self.img.width = self.w
        self.img.height = self.h

    def mouse_move(self, x, y, dx, dy):
        if self.is_inside(x + self.x, y + self.y) and self.mouse_c:
            cx, cy = self.on_plot(x, y)
            self.set_val('c', cx + cy * 1j)


class JuliaWindow(pyg.window.Window):
    def set_vars(self):
        self.valset.add_value('sz', .5)
        self.valset.add_value('max_iter', 24)
        self.valset.add_value('limit', 20.0)
        self.valset.add_value('c', -.25 -.67j)
        self.valset.add_value('calctime', 0.0)
        self.valset.add_value('flushtime', 0.0)

        main = JuliaScreen(0, 200, 500, 500, valset=self.valset)
        self.add_screen('main', main)

        self.add_float_field('zoomfield', 230, 55, 100, 15, 'Zoom', self.valset.get_obj('sz'), limit='ul', inclusive='', low=0, high=1)
        self.add_int_field('max_iter', 230, 155, 100, 15, 'Max Iter', self.valset.get_obj('max_iter'), limit='l', low=1)
        self.add_float_field('limit', 230, 135, 100, 15, 'Limit', self.valset.get_obj('limit'), limit='l', inclusive='', low=0)
        self.add_complex_field('c', 230, 75, 100, 15, 'C', self.valset.get_obj('c'))

        self.add_button('resetb', 150, 120, 40, 40, 'Reset', self.reset)
        self.add_button('mouse_c', 150, 60, 40, 40, 'Mouse C', self.toggle_mouse_c)
        self.add_button('m1b', 50, 130, 80, 20, 'Julia z^2+c', lambda: self.set_mode(0))
        self.add_button('m2b', 50, 100, 80, 20, 'Mandelbrot', lambda: self.set_mode(1))
        self.add_button('m3b', 50, 70, 80, 20, 'Julia z^3+c', lambda: self.set_mode(2))
        self.add_button('m4b', 50, 40, 80, 20, 'Julia c*sin(z)', lambda: self.set_mode(3))

        self.add_label('leftlabel', 10, 180, '%.5f' % (self.screens['main'].sx - self.screens['main'].sw / 2), color=(255, 0, 255))
        self.add_label('rightlabel', self.width- 60, 180, '%.5f' % (self.screens['main'].sx + self.screens['main'].sw / 2), color=(255, 0, 255))
        self.add_label('toplabel', 10, self.height + 180, '%.5f' % (self.screens['main'].sy + self.screens['main'].sh / 2), color=(255, 0, 255))
        self.add_label('bottomlabel', 10, 210, '%.5f' % (self.screens['main'].sy - self.screens['main'].sh / 2), color=(255, 0, 255))
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
        self.labels['leftlabel'].set_text('%.5f' % (self.screens['main'].sx - self.screens['main'].sw / 2))
        self.labels['rightlabel'].set_text('%.5f' % (self.screens['main'].sx + self.screens['main'].sw / 2))
        self.labels['rightlabel'].set_pos(self.width - 60, 180)
        self.labels['toplabel'].set_text('%.5f' % (self.screens['main'].sy + self.screens['main'].sh / 2))
        self.labels['toplabel'].set_pos(10, self.height + 180)
        self.labels['bottomlabel'].set_text('%.5f' % (self.screens['main'].sy - self.screens['main'].sh / 2))
        self.labels['calclabel'].set_text('  calc time: %.5f ms' % self.valset.get_val('calctime'))
        self.labels['calclabel'].set_pos(self.width - 160, 110)
        self.labels['flushlabel'].set_text(' flush time: %.5f ms' % self.valset.get_val('flushtime'))
        self.labels['flushlabel'].set_pos(self.width - 160, 90)

    def mouse_move(self, x, y, dx, dy):
        super().mouse_move(x, y, dx, dy)
        if self.screens['main'].mouse_c:
            self.fields['c'].update_label()
            self.screens['main'].render()


window = JuliaWindow(width=500, height=700, caption='Julia Graph', bg=(0, 0, 0, 1), resizable=True)
pyglet.app.run()
