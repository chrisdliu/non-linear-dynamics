import time

import numpy as np
import pyglet
from numba import jit, vectorize, guvectorize

import pyg
from Mandelbrot.emailer import email


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
        zmag2 = zr2 + zi2
        if zmag2 > limit2:
            return n + 1 - np.log2(np.log2(np.power(zmag2, .5)))
        zi = 2 * zr * zi + ci
        zr = zr2 - zi2 + cr
    return 0


@vectorize('float64(complex128, float64, int32)', target='parallel')
def mandel_z2_vec(c, limit, max_iter):
    limit2 = limit * limit
    zr = 0
    zi = 0
    cr = c.real
    ci = c.imag
    for n in range(max_iter):
        zr2 = zr * zr
        zi2 = zi * zi
        zmag2 = zr2 + zi2
        if zmag2 > limit2:
            return n + 1 - np.log2(np.log2(np.power(zmag2, .5)))
        zi = 2 * zr * zi + ci
        zr = zr2 - zi2 + cr
    return 0


@jit
def vectorize_call(mode, w, h, bl_x, bl_y, tr_x, tr_y, limit, max_iter, c, palette):
    zr = np.linspace(bl_x, tr_x, w, dtype=np.float64, endpoint=False)
    zi = np.linspace(bl_y, tr_y, h, dtype=np.float64, endpoint=False)
    z = zr[:, None] + zi * 1j  # [x][y]
    if mode != 1:
        color_data = julia_z2_vec(z, c, limit, max_iter)
    else:
        color_data = mandel_z2_vec(z, limit, max_iter)

    return parse_color_data(color_data, max_iter, palette)


@guvectorize('(float64[:], int32[:], int32[:,:], int32[:])', '(n),(),(p,q)->(n)', target='parallel')
def parse_color_data(color_data, max_iter, palette, output):
    div = max_iter[0] // 4
    for i in range(color_data.shape[0]):
        norm = color_data[i] / div
        intnorm = int(norm)
        c1 = palette[intnorm % len(palette)]
        c2 = palette[(intnorm + 1) % len(palette)]
        t = norm % 1
        r = int(c1[0] + (c2[0] - c1[0]) * t)
        g = int(c1[1] + (c2[1] - c1[1]) * t)
        b = int(c1[2] + (c2[2] - c1[2]) * t)
        output[i] = ((r & 0xff) << 16) | ((g & 0xff) << 8) | (b & 0xff)


@jit('int32(int32, int32, int32)')
def get_pos(x, y, w):
    return (y * w + x) * 3


@jit
def get_data(mode, w, h, bl_x, bl_y, tr_x, tr_y, limit, max_iter, c, palette, pixels):
    color_data = vectorize_call(mode, w, h, bl_x, bl_y, tr_x, tr_y, limit, max_iter, c, palette)
    for y in range(h):
        for x in range(w):
            idx = get_pos(x, y, w)
            color = color_data[x][y]
            pixels[idx] = (color >> 16) & 0xff
            pixels[idx + 1] = (color >> 8) & 0xff
            pixels[idx + 2] = color & 0xff


class JuliaScreen(pyg.screen.GraphScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mode = 1
        self.pixels = np.zeros(self.w * self.h * 3, dtype=np.ubyte)
        self.ctpixels = np.ctypeslib.as_ctypes(self.pixels)
        self.img = pyglet.image.ImageData(self.w, self.h, 'RGB', self.ctpixels)

        self.palette = np.array([[0, 0, 0], [100, 0, 100], [255, 255, 255], [255, 161, 3]], dtype=np.int32)

    def set_mode(self, mode):
        self.mode = mode
        self.reset_screen()
        self.resize(self.parent.width, self.parent.height)

    def reset_screen(self):
        self.set_val('max_iter', 24)
        self.parent.fields['max_iter'].update_label()
        super().reset_screen()

    def render(self):
        # calc
        start = time.time()
        bl_x, bl_y = self.on_plot(0, 0)
        tr_x, tr_y = self.on_plot(self.w, self.h)
        c = self.get_val('c')
        max_iter = self.get_val('max_iter')
        self.palette[self.get_val('pal_idx')] = [self.get_val('pal_r'), self.get_val('pal_g'), self.get_val('pal_b')]
        limit = self.get_val('limit')
        get_data(self.mode, self.w, self.h, bl_x, bl_y, tr_x, tr_y, limit, max_iter, c, self.palette, self.pixels)
        end = time.time()
        self.valset.set_val('calctime', ((end - start) * 1000))

        # flush
        start = time.time()
        self.img.set_data('RGB', self.img.width * 3, self.ctpixels)
        end = time.time()
        self.valset.set_val('flushtime', ((end - start) * 1000))

    def draw(self):
        self.img.blit(self.x, self.y)

    def resize(self, width, height):
        if self.mode != 2:
            self.refit(width, height - 200)
        else:
            self.refit(width // 2, height - 200)

        del self.img, self.pixels, self.ctpixels
        self.pixels = np.zeros(self.w * self.h * 3, dtype=np.ubyte)
        self.ctpixels = np.ctypeslib.as_ctypes(self.pixels)
        self.img = pyglet.image.ImageData(self.w, self.h, 'RGB', self.ctpixels)

    def mouse_move(self, x, y, dx, dy):
        if self.mode != 2 and self.is_inside(x + self.x, y + self.y) and self.get_val('mouse_c'):
            cx, cy = self.on_plot(x, y)
            self.set_val('c', cx + cy * 1j)


class MandelScreen(pyg.screen.GraphScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pixels = np.zeros(self.w * self.h * 3, dtype=np.ubyte)
        self.ctpixels = np.ctypeslib.as_ctypes(self.pixels)
        self.img = pyglet.image.ImageData(self.w, self.h, 'RGB', self.ctpixels)

        self.palette = np.array([[0, 0, 0], [100, 0, 100], [255, 255, 255], [255, 161, 3]], dtype=np.int32)

    def reset_screen(self):
        super().reset_screen()

    def render(self):
        # calc
        bl_x, bl_y = self.on_plot(0, 0)
        tr_x, tr_y = self.on_plot(self.w, self.h)
        c = self.get_val('c')
        max_iter = self.get_val('max_iter')
        self.palette[self.get_val('pal_idx')] = [self.get_val('pal_r'), self.get_val('pal_g'), self.get_val('pal_b')]
        limit = self.get_val('limit')
        get_data(1, self.w, self.h, bl_x, bl_y, tr_x, tr_y, limit, max_iter, c, self.palette, self.pixels)

        # flush
        self.img.set_data('RGB', self.img.width * 3, self.ctpixels)

    def draw(self):
        self.img.blit(self.x, self.y)

    def resize(self, width, height):
        self.refit(width // 2, height - 200)

        del self.img, self.pixels, self.ctpixels
        self.pixels = np.zeros(self.w * self.h * 3, dtype=np.ubyte)
        self.ctpixels = np.ctypeslib.as_ctypes(self.pixels)
        self.img = pyglet.image.ImageData(self.w, self.h, 'RGB', self.ctpixels)

        self.set_pos(width // 2, 200)

    def mouse_move(self, x, y, dx, dy):
        if self.is_inside(x + self.x, y + self.y) and self.get_val('mouse_c'):
            cx, cy = self.on_plot(x, y)
            self.set_val('c', cx + cy * 1j)

    def mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        pass

    def key_down(self, symbol, modifiers):
        pass


def rdim(x, y, w, h):
    return x, y, x + w, y, x + w, y + h, x, y + h


class ColorBox(pyg.gui.Box):
    def __init__(self, parent, name, x, y, width, height, palette):
        super().__init__(parent, name, x, y, width, height)
        self.palette = palette

    def render(self):
        self.add_quad(*rdim(self.x + 2, self.y + 2, 26, 26), color=[*self.palette[0]])
        self.add_quad(*rdim(self.x + 32, self.y + 2, 26, 26), color=[*self.palette[1]])
        self.add_quad(*rdim(self.x + 62, self.y + 2, 26, 26), color=[*self.palette[2]])
        self.add_quad(*rdim(self.x + 92, self.y + 2, 26, 26), color=[*self.palette[3]])
        offset = self.parent.get_val('pal_idx') * 30
        self.add_quad(*rdim(self.x + offset, self.y, 2, 30), color=(255, 255, 255))
        self.add_quad(*rdim(self.x + 28 + offset, self.y, 2, 30), color=(255, 255, 255))
        self.add_quad(*rdim(self.x + 2 + offset, self.y + 28, 26, 2), color=(255, 255, 255))
        self.add_quad(*rdim(self.x + 2 + offset, self.y, 26, 2), color=(255, 255, 255))
        self.flush()


class JuliaWindow(pyg.window.Window):
    def set_vars(self):
        """
        Adds the gui components
        """
        self.valset.add_float_value('gz', .5, limit='ul', inclusive='', low=0, high=1)
        self.valset.add_int_value('max_iter', 24, limit='l', low=1)
        self.valset.add_float_value('limit', 20.0, limit='l', inclusive='', low=0)
        self.valset.add_complex_value('c', -.25 - .67j)
        self.valset.add_float_value('calctime', 0)
        self.valset.add_float_value('flushtime', 0)
        self.valset.add_int_value('pal_idx', 0, limit='ul', low=0, high=3)
        self.valset.add_int_value('pal_r', 0)
        self.valset.add_int_value('pal_g', 0)
        self.valset.add_int_value('pal_b', 0)
        self.valset.add_bool_value('mouse_c', False)
        self.valset.add_float_value('saved_gx', 0)
        self.valset.add_float_value('saved_gy', 0)
        self.valset.add_float_value('saved_gw', 0)
        self.valset.add_float_value('saved_gh', 0)

        main = JuliaScreen(self, 0, 200, 500, 500, 0, 0, 5, 5, 'gz')
        self.add_screen('main', main)
        mandel = MandelScreen(self, 250, 200, 250, 500, 0, 0, 2.5, 5, 'gz')
        mandel.off()
        self.add_screen('mandel', mandel)

        self.add_button('m0b', 10, 130, 80, 15, 'Julia', lambda: self.set_mode(0))
        self.add_button('m1b', 10, 110, 80, 15, 'Mandelbrot', lambda: self.set_mode(1))
        self.add_button('m7b', 10, 90, 80, 15, 'Both', lambda: self.set_mode(2))
        self.add_button('resetb', 10, 10, 50, 45, 'Reset\nScreen\nView(r)', self.reset)
        self.add_toggle_button('mouse_c', 80, 10, 50, 30, 'Mouse\nSet C(c)', self.get_valobj('mouse_c'))
        self.buttons['mouse_c'].off()

        self.add_int_field('max_iter', 150, 180, 120, 15, 'Max Iter', self.get_valobj('max_iter'))
        self.add_label('c', 150, 150)

        self.add_button('pal_left', 150, 5, 55, 15, 'Left', self.palette_left)
        self.add_button('pal_right', 215, 5, 55, 15, 'Right', self.palette_right)
        self.add_int_hslider('pal_r', 150, 70, 120, 15, 'Red  ', self.get_valobj('pal_r'), 0, 255, lambda: self.boxes['colorbox'].render())
        self.add_int_hslider('pal_g', 150, 50, 120, 15, 'Green', self.get_valobj('pal_g'), 0, 255, lambda: self.boxes['colorbox'].render())
        self.add_int_hslider('pal_b', 150, 30, 120, 15, 'Blue ', self.get_valobj('pal_b'), 0, 255, lambda: self.boxes['colorbox'].render())
        self.add_box('colorbox', ColorBox(self, 'colorbox', 150, 90, 120, 30, self.screens['main'].palette))
        self.add_label('pal_label', 160, 125, 'Palette:')

        self.add_string_value('email')
        self.add_string_field('email', 300, 80, 180, 15, 'Email', self.get_valobj('email'))
        self.add_button('clearemail', 350, 30, 40, 30, 'Clear\nEmail', self.clear_email)
        self.add_button('sendimage', 300, 30, 40, 30, 'Send\nImage', self.send_image)

        self.add_label('leftlabel', color=(255, 0, 255))
        self.add_label('rightlabel', color=(255, 0, 255))
        self.add_label('toplabel', color=(255, 0, 255))
        self.add_label('bottomlabel', color=(255, 0, 255))
        self.add_label('zoomlabel')

        self.add_label('calclabel', color=(0, 240, 120))
        self.add_label('flushlabel', color=(0, 240, 120))

    def send_image(self):
        self.screens['main'].img.save('screen.png')
        email(self.get_val('email'))

    def clear_email(self):
        self.fields['email'].clear()

    def palette_left(self):
        self.get_valobj('pal_idx').decr()
        self.palette_shift()

    def palette_right(self):
        self.get_valobj('pal_idx').incr()
        self.palette_shift()

    def palette_shift(self):
        pal_idx = self.get_val('pal_idx')
        main = self.get_screen('main')
        self.set_val('pal_r', main.palette[pal_idx][0])
        self.set_val('pal_g', main.palette[pal_idx][1])
        self.set_val('pal_b', main.palette[pal_idx][2])
        self.get_slider('pal_r').update()
        self.get_slider('pal_g').update()
        self.get_slider('pal_b').update()
        self.boxes['colorbox'].render()
        self.update_labels()

    def reset(self):
        self.screens['main'].reset_screen()
        if self.screens['main'].mode == 7:
            self.screens['mandel'].reset_screen()

    def set_mode(self, mode):
        if mode == self.screens['main'].mode:
            return
        if mode == 2:
            self.labels['leftlabel'].off()
            self.labels['rightlabel'].off()
            self.labels['toplabel'].off()
            self.labels['bottomlabel'].off()
            self.labels['c'].on()
            self.buttons['mouse_c'].on()
            self.screens['mandel'].on()
        else:
            if mode == 0:
                self.labels['leftlabel'].on()
                self.labels['rightlabel'].on()
                self.labels['toplabel'].on()
                self.labels['bottomlabel'].on()
                self.labels['c'].on()
                self.buttons['mouse_c'].on()
                self.screens['mandel'].on()
            else:
                self.labels['leftlabel'].on()
                self.labels['rightlabel'].on()
                self.labels['toplabel'].on()
                self.labels['bottomlabel'].on()
                self.labels['c'].off()
                if self.get_val('mouse_c'):
                    self.buttons['mouse_c'].toggle()
                self.buttons['mouse_c'].off()
            self.screens['mandel'].off()
        self.screens['main'].set_mode(mode)
        self.on_resize(self.width, self.height)

    def update_labels(self):
        self.labels['leftlabel'].set_text('%.5E' % self.get_screen('main').min_gx)
        self.labels['leftlabel'].set_pos(10, 180)
        self.labels['rightlabel'].set_text('%.5E' % self.get_screen('main').max_gx)
        self.labels['rightlabel'].set_pos(self.width - 80, 180)
        self.labels['toplabel'].set_text('%.5f' % self.get_screen('main').max_gy)
        self.labels['toplabel'].set_pos(10, self.height - 20)
        self.labels['bottomlabel'].set_text('%.5f' % self.get_screen('main').min_gy)
        self.labels['bottomlabel'].set_pos(10, 210)
        self.labels['zoomlabel'].set_pos(self.width * 3 // 5, 180)
        self.labels['zoomlabel'].set_text('Zoom: %.5E' % self.get_screen('main').total_zoom)
        self.labels['c'].set_text('C: %s' % str(self.get_val('c')))

        self.labels['calclabel'].set_text('  calc time: %.3f ms' % self.valset.get_val('calctime'))
        self.labels['calclabel'].set_pos(self.width - 160, 165)
        self.labels['flushlabel'].set_text(' flush time: %.3f ms' % self.valset.get_val('flushtime'))
        self.labels['flushlabel'].set_pos(self.width - 160, 150)

    def mouse_move(self, x, y, dx, dy):
        super().mouse_move(x, y, dx, dy)
        if self.get_val('mouse_c'):
            self.screens['main'].render()

    def mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        super().mouse_drag(x, y, dx, dy, buttons, modifiers)
        if isinstance(self.focus, pyg.gui.Slider):
            self.screens['main'].render()

    def key_down(self, symbol, modifiers):
        super().key_down(symbol, modifiers)
        if not self.focus:
            if symbol == pyglet.window.key.C:
                self.get_button('mouse_c').toggle()
            if symbol == pyglet.window.key.R:
                self.reset()


pyg.run(JuliaWindow, 500, 700, caption='Mandelbrot Explorer')
