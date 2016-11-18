import pyg
import pyglet
import numpy as np
from numba import jit, vectorize, guvectorize
import math
import time
import ctypes


@jit('float64(int32, float64)')
def norm_z3(iter, mag):
    ln3 = np.log(3)
    return iter + 1 - np.log(np.log(mag) / ln3) / (ln3 * ln3)
    #return (iter + 1 - math.log(math.log(mag, 3), 3))
    #return iter + 1 - np.log2(np.log2(mag))


@jit('int64(complex128, complex128, float64, int64)')
def get_color_z3(z, c, limit, max_iter):
    for n in range(max_iter):
        if np.abs(z) > limit:
            return norm_z3(n, np.abs(z))
        z = z * z * z + c
    return 0


@vectorize('float64(complex128, float64, int32)', target='parallel')  # using guvectorize takes the same time
def mandel_vec(z, limit, max_iter):
    limit2 = limit * limit
    zr = z.real
    zi = z.imag
    cr = z.real
    ci = z.imag
    for n in range(max_iter):
        zr2 = zr * zr
        zi2 = zi * zi
        if zr2 + zi2 > limit2:
            return n + 1 - np.log2(np.log2(np.power(zr2 + zi2, .5)))
        zi = 2 * zr * zi + ci
        zr = zr2 - zi2 + cr
    return 0


@vectorize('float64(complex128, complex128, float64, int32)', target='parallel')
def julia_z2_vec(z, c, limit, max_iter):
    limit2 = limit * limit
    zr = z.real
    zi = z.imag
    cr = c.real
    ci = c.imag
    for n in range(max_iter):
        zr2 = zr * zr
        zi2 = zi * zi
        if zr2 + zi2 > limit2:
            return n + 1 - np.log2(np.log2(np.power(zr2 + zi2, .5)))
        zi = 2 * zr * zi + ci
        zr = zr2 - zi2 + cr
    return 0


@vectorize('float64(complex128, complex128, float64, int32)', target='parallel')
def julia_z3_vec(z, c, limit, max_iter):
    return get_color_z3(z, c, limit, max_iter)


@jit
def get_data_call(mode, w, h, bl_x, bl_y, tr_x, tr_y, limit, max_iter, c, palette):
    zr = np.linspace(bl_x, tr_x, w, dtype=np.float64, endpoint=False)
    zi = np.linspace(bl_y, tr_y, h, dtype=np.float64, endpoint=False)
    z = zr[:,None] + zi * 1j  # [y, bottom to top][x, left to right]
    if mode == 0:
        color_data = julia_z2_vec(z, c, limit, max_iter)
    elif mode == 1:
        color_data = mandel_vec(z, limit, max_iter) #ndarray, shape=w,h
    elif mode == 2:
        color_data = julia_z3_vec(z, c, limit, max_iter)

    return parse_color_data(color_data, palette)


@guvectorize('(float64[:], int32[:,:], int32[:])', '(n),(p,q)->(n)', target='parallel')
def parse_color_data(color_data, palette, output):
    for i in range(color_data.shape[0]):
        norm = color_data[i]
        intnorm = int(norm)
        c1 = palette[intnorm % len(palette)]
        c2 = palette[(intnorm + 1) % len(palette)]
        t = norm % 1
        r = int(c1[0] + (c2[0] - c1[0]) * t)
        g = int(c1[1] + (c2[1] - c1[1]) * t)
        b = int(c1[2] + (c2[2] - c1[2]) * t)
        output[i] = ((r & 0xff) << 16) | ((g & 0xff) << 8) | (b & 0xff)


@jit
def get_pos(x, y, w):
    return (y * w + x) * 3


@jit
def get_data(mode, w, h, bl_x, bl_y, tr_x, tr_y, limit, max_iter, c, palette):
    color_data = get_data_call(mode, w, h, bl_x, bl_y, tr_x, tr_y, limit, max_iter, c, palette)
    idx_max = w * h * 3
    colors = np.zeros(idx_max, dtype=np.int16)
    for y in range(h):
        for x in range(w):
            idx = get_pos(x, y, w)
            color = color_data[x][y]
            colors[idx] = (color >> 16) & 0xff
            colors[idx + 1] = (color >> 8) & 0xff
            colors[idx + 2] = color & 0xff
    return colors


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


class JuliaScreen(pyg.screen.GraphScreen):
    def __init__(self, x, y, width, height, bg=(255, 255, 255), valset=None, visible=True):
        self.mode = 1
        super().__init__(x, y, width, height, 0, 0, 5, 5, bg=bg, valset=valset, visible=visible)
        rawdata = np.zeros(self.w * self.h * 3, dtype=np.ubyte)
        self.img = pyglet.image.ImageData(self.w, self.h, 'RGB', rawdata)

    def set_mode(self, mode):
        self.mode = mode

    def render(self):
        #calc
        start = time.time()
        bl_x, bl_y = self.on_plot(0, 0)
        tr_x, tr_y = self.on_plot(self.w, self.h)
        c = self.get_val('c')
        max_iter = self.get_val('max_iter')
        global palette, palette_colors
        palette_colors[0] = [self.get_val('palette0r'), self.get_val('palette0g'), self.get_val('palette0b')]
        palette_colors[1] = [self.get_val('palette1r'), self.get_val('palette1g'), self.get_val('palette1b')]
        palette_colors[2] = [self.get_val('palette2r'), self.get_val('palette2g'), self.get_val('palette2b')]
        palette_colors[3] = [self.get_val('palette3r'), self.get_val('palette3g'), self.get_val('palette3b')]
        if len(palette) != max_iter:
            palette = set_palette(max_iter)
        limit = self.get_val('limit')
        colors = get_data(self.mode, self.w, self.h, bl_x, bl_y, tr_x, tr_y, limit, max_iter, c, palette)
        end = time.time()
        self.valset.set_val('calctime', ((end - start) * 1000))

        #flush
        start = time.time()
        c_ubyte_p = ctypes.POINTER(ctypes.c_ubyte)
        colors_ubyte = colors.astype(np.ubyte)
        rawdata = colors_ubyte.ctypes.data_as(c_ubyte_p)
        self.img.set_data('RGB', self.img.width * 3, rawdata)
        end = time.time()
        self.valset.set_val('flushtime', ((end - start) * 1000))

    def on_draw(self):
        super().on_draw()
        self.img.blit(self.x, self.y)

    def resize(self, width, height):
        self.refit(width, height - 300)
        self.img.width = self.w
        self.img.height = self.h
        print((self.w, self.h))

    def mouse_move(self, x, y, dx, dy):
        if self.is_inside(x + self.x, y + self.y) and self.get_val('mouse_c'):
            cx, cy = self.on_plot(x, y)
            self.set_val('c', cx + cy * 1j)


class JuliaWindow(pyg.window.Window):
    def set_vars(self):
        self.valset.add_float_value('sz', .5, limit='ul', inclusive='', low=0, high=1)
        self.valset.add_int_value('max_iter', 24, limit='l', low=1)
        self.valset.add_float_value('limit', 20.0, limit='l', inclusive='', low=0)
        self.valset.add_complex_value('c', -.25 -.67j)
        self.valset.add_float_value('calctime', 0.0)
        self.valset.add_float_value('flushtime', 0.0)
        self.valset.add_int_value('palette0r', 0)
        self.valset.add_int_value('palette0g', 0)
        self.valset.add_int_value('palette0b', 0)
        self.valset.add_int_value('palette1r', 100)
        self.valset.add_int_value('palette1g', 0)
        self.valset.add_int_value('palette1b', 100)
        self.valset.add_int_value('palette2r', 255)
        self.valset.add_int_value('palette2g', 255)
        self.valset.add_int_value('palette2b', 255)
        self.valset.add_int_value('palette3r', 255)
        self.valset.add_int_value('palette3g', 161)
        self.valset.add_int_value('palette3b', 3)
        self.valset.add_bool_value('mouse_c', False)

        main = JuliaScreen(0, 300, 500, 500, valset=self.valset)
        self.add_screen('main', main)

        self.add_float_field('zoomfield', 120, 30, 120, 15, 'Zoom', self.get_valobj('sz'))
        self.add_int_field('max_iter', 120, 180, 120, 15, 'Max Iter', self.get_valobj('max_iter'))
        self.add_float_field('limit', 120, 160, 120, 15, 'Limit', self.get_valobj('limit'))
        self.add_complex_field('c', 120, 140, 120, 15, 'C', self.get_valobj('c'))

        self.add_button('resetb', 20, 30, 40, 15, 'Reset', self.reset)
        #self.add_button('mouse_c', 65, 30, 40, 15, 'Mouse C', self.toggle_mouse_c)
        self.add_button('m1b', 20, 150, 80, 20, 'Julia z^2+c', lambda: self.set_mode(0))
        self.add_button('m2b', 20, 120, 80, 20, 'Mandelbrot', lambda: self.set_mode(1))
        self.add_button('m3b', 20, 90, 80, 20, 'Julia z^3+c', lambda: self.set_mode(2))
        self.add_toggle_button('mouse_c', 65, 30, 40, 15, 'Mouse C', self.get_valobj('mouse_c'))

        self.add_label('leftlabel', 10, 280, '%.5f' % (self.screens['main'].sx - self.screens['main'].sw / 2), color=(255, 0, 255))
        self.add_label('rightlabel', self.width- 60, 280, '%.5f' % (self.screens['main'].sx + self.screens['main'].sw / 2), color=(255, 0, 255))
        self.add_label('toplabel', 10, self.height + 180, '%.5f' % (self.screens['main'].sy + self.screens['main'].sh / 2), color=(255, 0, 255))
        self.add_label('bottomlabel', 10, 310, '%.5f' % (self.screens['main'].sy - self.screens['main'].sh / 2), color=(255, 0, 255))

        self.add_label('calclabel', self.width - 160, 160, '  calc time: %.5f' % self.valset.get_val('calctime'))
        self.add_label('flushlabel', self.width - 160, 145, ' flush time: %.5f' % self.valset.get_val('flushtime'))
        self.add_label('srikarlabel', self.width // 2, 4, 'srikar')

        self.add_int_slider('palette0r', 260, 240, 120, 15, 0, 'Pal 0 R', self.get_valobj('palette0r'), low=0, high=255)
        self.add_int_slider('palette0g', 260, 220, 120, 15, 0, 'Pal 0 G', self.get_valobj('palette0g'), low=0, high=255)
        self.add_int_slider('palette0b', 260, 200, 120, 15, 0, 'Pal 0 B', self.get_valobj('palette0b'), low=0, high=255)
        self.add_int_slider('palette1r', 260, 180, 120, 15, 0, 'Pal 1 R', self.get_valobj('palette1r'), low=0, high=255)
        self.add_int_slider('palette1g', 260, 160, 120, 15, 0, 'Pal 1 G', self.get_valobj('palette1g'), low=0, high=255)
        self.add_int_slider('palette1b', 260, 140, 120, 15, 0, 'Pal 1 B', self.get_valobj('palette1b'), low=0, high=255)
        self.add_int_slider('palette2r', 260, 120, 120, 15, 0, 'Pal 2 R', self.get_valobj('palette2r'), low=0, high=255)
        self.add_int_slider('palette2g', 260, 100, 120, 15, 0, 'Pal 2 G', self.get_valobj('palette2g'), low=0, high=255)
        self.add_int_slider('palette2b', 260,  80, 120, 15, 0, 'Pal 2 B', self.get_valobj('palette2b'), low=0, high=255)
        self.add_int_slider('palette3r', 260,  60, 120, 15, 0, 'Pal 3 R', self.get_valobj('palette3r'), low=0, high=255)
        self.add_int_slider('palette3g', 260,  40, 120, 15, 0, 'Pal 3 G', self.get_valobj('palette3g'), low=0, high=255)
        self.add_int_slider('palette3b', 260,  20, 120, 15, 0, 'Pal 3 B', self.get_valobj('palette3b'), low=0, high=255)


    def reset(self):
        self.screens['main'].reset()

    def set_mode(self, mode):
        if mode == self.screens['main'].mode:
            return
        self.screens['main'].set_mode(mode)
        self.render()

    def update_labels(self):
        self.labels['leftlabel'].set_text('%.5f' % (self.screens['main'].sx - self.screens['main'].sw / 2))
        self.labels['rightlabel'].set_text('%.5f' % (self.screens['main'].sx + self.screens['main'].sw / 2))
        self.labels['rightlabel'].set_pos(self.width - 60, 280)
        self.labels['toplabel'].set_text('%.5f' % (self.screens['main'].sy + self.screens['main'].sh / 2))
        self.labels['toplabel'].set_pos(10, self.height - 20)
        self.labels['bottomlabel'].set_text('%.5f' % (self.screens['main'].sy - self.screens['main'].sh / 2))

        self.labels['calclabel'].set_text('  calc time: %.5f ms' % self.valset.get_val('calctime'))
        self.labels['calclabel'].set_pos(self.width - 160, 160)
        self.labels['flushlabel'].set_text(' flush time: %.5f ms' % self.valset.get_val('flushtime'))
        self.labels['flushlabel'].set_pos(self.width - 160, 145)

    def mouse_move(self, x, y, dx, dy):
        super().mouse_move(x, y, dx, dy)
        if self.get_val('mouse_c'):
            self.fields['c'].update_label()
            self.screens['main'].render()

    def key_down(self, symbol, modifiers):
        super().key_down(symbol, modifiers)
        if not self.focus:
            if symbol == pyglet.window.key.C:
                self.get_button('mouse_c').toggle()

window = JuliaWindow(width=500, height=800, caption='Julia Graph', bg=(0, 0, 0, 1), resizable=True)
pyglet.app.run()
