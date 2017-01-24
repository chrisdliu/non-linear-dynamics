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


@vectorize('float64(complex128, complex128, float64, int32)', target='parallel')
def julia_z2_vec(z, c, limit, max_iter):
    """
    Calculates orbit of z under T(z) = z^2 + c with z and c as the input
    :param z: z
    :param c: c
    :param limit: escape radius
    :param max_iter: maximum iterations
    :return: normalized escape iteration
    """
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



@vectorize('float64(complex128, float64, int32)', target='parallel')  # using guvectorize takes the same time
def mandel_z2_vec(c, limit, max_iter):
    """
    Calculates orbit of 0 under T(z) = z^2 + c with c as the input
    :param c: c
    :param limit: escape radius
    :param max_iter: maximum iterations
    :return: normalized escape iteration
    """
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


@vectorize('float64(complex128, complex128, float64, int32)', target='parallel')
def julia_z3_vec(z, c, limit, max_iter):
    for n in range(max_iter):
        zmag = np.abs(z)
        if zmag > limit:
            return n + 1 - np.log2(np.log2(zmag)) / np.log2(3)
        z = z * z * z + c
    return 0


@vectorize('float64(complex128, float64, int32)', target='parallel')
def mandel_z3_vec(c, limit, max_iter):
    z = 0
    for n in range(max_iter):
        zmag = np.abs(z)
        if zmag > limit:
            return n + 1 - np.log2(np.log2(zmag)) / np.log2(3)
        z = z * z * z + c
    return 0


@vectorize('float64(complex128, complex128, float64, int32)', target='parallel')
def julia_z15_vec(z, c, limit, max_iter):
    for n in range(max_iter):
        zmag = np.abs(z)
        if zmag > limit:
            return n + 1 - np.log2(np.log2(zmag)) / np.log2(1.5)
        z = np.power(z, 1.5) + c
    return 0


@vectorize('float64(complex128, float64, int32)', target='parallel')
def mandel_z15_vec(c, limit, max_iter):
    z = 0
    for n in range(max_iter):
        zmag = np.abs(z)
        if zmag > limit:
            return n + 1 - np.log2(np.log2(zmag)) / np.log2(1.5)
        z = np.power(z, 1.5) + c
    return 0


@vectorize('float64(complex128, complex128, float64, int32)', target='parallel')
def julia_sin_vec(z, c, limit, max_iter):
    for n in range(max_iter):
        zmag = np.abs(z)
        if zmag > limit:
            return n
        z = c * np.sin(z)
    return 0


@jit
def vectorize_call(mode, w, h, bl_x, bl_y, tr_x, tr_y, limit, max_iter, c, palette):
    """
    Calls the vectorized function according to the mode
    0 - filled julia set of z^2 + c
    1 - mandelbrot set of z^2 + c
    2 - filled julia set of z^3 + c
    Returns a 2d RGB array
    :param mode: mode
    :param w: screen width
    :param h: screen height
    :param bl_x: bottom left x coordinate of the graph
    :param bl_y: bottom left y coordinate of the graph
    :param tr_x: top right x coordinate of the graph
    :param tr_y: top right y coordinate of the graph
    :param limit: escape radius
    :param max_iter: maximum iterations
    :param c: c
    :param palette: color palette
    :return: 2d RGB array
    """
    zr = np.linspace(bl_x, tr_x, w, dtype=np.float64, endpoint=False)
    zi = np.linspace(bl_y, tr_y, h, dtype=np.float64, endpoint=False)
    z = zr[:, None] + zi * 1j  # [x][y]
    if mode in [0, 7]:
        color_data = julia_z2_vec(z, c, limit, max_iter)
    elif mode == 1:
        color_data = mandel_z2_vec(z, limit, max_iter)
    elif mode == 2:
        color_data = julia_z3_vec(z, c, limit, max_iter)
    elif mode == 3:
        color_data = mandel_z3_vec(z, limit, max_iter)
    elif mode == 4:
        color_data = julia_z15_vec(z, c, limit, max_iter)
    elif mode == 5:
        color_data = mandel_z15_vec(z, limit, max_iter)
    else:
        color_data = julia_sin_vec(z, c, limit, max_iter)

    return parse_color_data(color_data, max_iter, palette)


@guvectorize('(float64[:], int32[:], int32[:,:], int32[:])', '(n),(),(p,q)->(n)', target='parallel')
def parse_color_data(color_data, max_iter, palette, output):
    """
    Turns an array of normalized escape iterations into an array of RGB colors according to the palette
    :param color_data: array of normalized escape iterations
    :param max_iter: maximum iterations
    :param palette: color palette
    :param output: the array of RGB colors
    """
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
def get_data(mode, w, h, bl_x, bl_y, tr_x, tr_y, limit, max_iter, c, palette):
    """
    Passes arguments to vectorize_call() since it can't have a for loop without breaking for some stupid reason
    Then converts and returns the 2d RGB array into a 1d RGB array with separate RGB values
    :param mode: mode
    :param w: screen width
    :param h: screen height
    :param bl_x: bottom left x coordinate of the graph
    :param bl_y: bottom left y coordinate of the graph
    :param tr_x: top right x coordinate of the graph
    :param tr_y: top right y coordinate of the graph
    :param limit: escape radius
    :param max_iter: maximum iterations
    :param c: c
    :param palette: color palette
    :return: 1d RGB array with separate RGB values
    """
    color_data = vectorize_call(mode, w, h, bl_x, bl_y, tr_x, tr_y, limit, max_iter, c, palette)
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


class MandelScreen(pyg.screen.GraphScreen):
    def __init__(self, x, y, width, height, valset, zoom_valobj, bg = (255, 255, 255), visible = True):
        super().__init__(x, y, width, height, 0, 0, 2.5, 5, valset, zoom_valobj, bg=bg, visible=visible)
        self.palette = np.array([[0, 0, 0], [100, 0, 100], [255, 255, 255], [255, 161, 3]], dtype=np.int32)

    def reset_screen(self):
        """
        Resets the graph
        """
        self.set_val('max_iter', 24)
        super().reset_screen()

    def render(self):
        """
        Renders the screen and creates an image with the pixel data
        """
        #calc
        start = time.time()
        bl_x, bl_y = self.on_plot(0, 0)
        tr_x, tr_y = self.on_plot(self.w, self.h)
        c = self.get_val('c')
        max_iter = self.get_val('max_iter')
        self.palette[self.get_val('pal_idx')] = [self.get_val('pal_r'), self.get_val('pal_g'), self.get_val('pal_b')]
        limit = self.get_val('limit')
        colors = get_data(1, self.w, self.h, bl_x, bl_y, tr_x, tr_y, limit, max_iter, c, self.palette)
        end = time.time()

        #flush
        start = time.time()
        points = []
        point_colors = []
        for i in range(self.w):
            for j in range(self.h):
                idx = get_pos(i, j, self.w)
                points.extend([i, j, 0])
                point_colors.extend([colors[idx], colors[idx + 1], colors[idx + 2]])
        self.set_points_both(points, point_colors)
        self.flush()
        end = time.time()

    def draw(self):
        """
        Draws the image created in render()
        """
        super().draw()

    def resize(self, width, height):
        self.refit(width // 2, height - 200)
        self.set_pos(width // 2, 200)

    def mouse_move(self, x, y, dx, dy):
        if self.is_inside(x + self.x, y + self.y) and self.get_val('mouse_c'):
            cx, cy = self.on_plot(x, y)
            self.set_val('c', cx + cy * 1j)

    def mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        pass

    def key_down(self, symbol, modifiers):
        pass


class JuliaScreen(pyg.screen.GraphScreen):
    def __init__(self, x, y, width, height, valset, zoom_valobj, bg=(255, 255, 255), visible=True):
        self.mode = 1
        super().__init__(x, y, width, height, 0, 0, 5, 5, valset, zoom_valobj, bg=bg, visible=visible)
        # -.743643887037151, 0.131825904205330, .000000000051299, .000000000051299
        rawdata = np.zeros(self.w * self.h * 3, dtype=np.ubyte).ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte))
        self.img = pyglet.image.ImageData(self.w, self.h, 'RGB', rawdata)

        self.palette = np.array([[0, 0, 0], [100, 0, 100], [255, 255, 255], [255, 161, 3]], dtype=np.int32)

    def set_mode(self, mode):
        """
        Sets the mode and resets
        :param mode: mode
        """
        self.mode = mode
        self.reset_screen()

    def reset_screen(self):
        """
        Resets the graph
        """
        self.set_val('max_iter', 24)
        super().reset_screen()

    def render(self):
        """
        Renders the screen and creates an image with the pixel data
        """
        #calc
        start = time.time()
        bl_x, bl_y = self.on_plot(0, 0)
        tr_x, tr_y = self.on_plot(self.w, self.h)
        c = self.get_val('c')
        max_iter = self.get_val('max_iter')
        self.palette[self.get_val('pal_idx')] = [self.get_val('pal_r'), self.get_val('pal_g'), self.get_val('pal_b')]
        limit = self.get_val('limit')
        colors = get_data(self.mode, self.w, self.h, bl_x, bl_y, tr_x, tr_y, limit, max_iter, c, self.palette)
        end = time.time()
        self.valset.set_val('calctime', ((end - start) * 1000))

        #flush
        start = time.time()
        if self.mode != 7:
            # convert to ctypes ubyte array
            del self.img
            rawdata = colors.astype(np.ubyte).ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte))
            self.img = pyglet.image.ImageData(self.w, self.h, 'RGB', rawdata)
        else:
            points = []
            point_colors = []
            for i in range(self.w):
                for j in range(self.h):
                    idx = get_pos(i, j, self.w)
                    points.extend([i, j, 0])
                    point_colors.extend([colors[idx], colors[idx + 1], colors[idx + 2]])
            self.set_points_both(points, point_colors)
            self.flush()
        end = time.time()
        self.valset.set_val('flushtime', ((end - start) * 1000))

    def draw(self):
        """
        Draws the image created in render()
        """
        #super().draw()
        if self.mode != 7:
            self.img.blit(self.x, self.y)
        else:
            super().draw()

    def resize(self, width, height):
        if self.mode != 7:
            self.refit(width, height - 200)
        else:
            self.refit(width // 2, height - 200)

    def mouse_move(self, x, y, dx, dy):
        if self.is_inside(x + self.x, y + self.y) and self.get_val('mouse_c'):
            cx, cy = self.on_plot(x, y)
            self.set_val('c', cx + cy * 1j)

    def mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        pass


class JuliaWindow(pyg.window.Window):
    def load_graph_coords(self):
        """
        Loads saved graph coordinates
        """
        try:
            file = open('julia_graph_coords.txt', 'r')
        except FileNotFoundError:
            self.default_graph_coords()
            return
        line = file.readline()
        while line:
            line = line.replace('\n', '')
            args = line.split(',')
            coords_mode = int(args[0])
            if coords_mode in [0, 2, 4, 6]:
                gx = float(args[1])
                gy = float(args[2])
                zoom = float(args[3])
                max_iter = int(args[4])
                c = complex(args[5])
                self.saved_coords[coords_mode].append([gx, gy, zoom, max_iter, c])
            elif coords_mode in [1, 3, 5]:
                gx = float(args[1])
                gy = float(args[2])
                zoom = float(args[3])
                max_iter = int(args[4])
                self.saved_coords[coords_mode].append([gx, gy, zoom, max_iter])
            line = file.readline()

    def default_graph_coords(self):
        """
        Creates a default graph coordinate file
        """
        file = open('julia_graph_coords.txt', 'w')
        #file.write('1,-.743643887037151,0.131825904205330,.000000000051299,.000000000051299')
        file.write('1,-.743643887037151,0.131825904205330,9500000000000000000000,5000')
        file.close()
        self.load_graph_coords()

    def save_graph_coords(self):
        """
        Saves graph coordinates
        """
        file = open('julia_graph_coords.txt', 'w')
        for mode in [0, 2, 4, 6]:
            for i in range(len(self.saved_coords[mode])):
                file.write('%i,%s,%s,%s,%i,%s\n' % (mode, self.saved_coords[mode][i][0], self.saved_coords[mode][i][1],
                                                    self.saved_coords[mode][i][2], self.saved_coords[mode][i][3],
                                                    self.saved_coords[mode][i][4]))
        for mode in [1, 3, 5]:
            for i in range(len(self.saved_coords[mode])):
                file.write('%i,%s,%s,%s,%i\n' % (mode, self.saved_coords[mode][i][0], self.saved_coords[mode][i][1],
                                                 self.saved_coords[mode][i][2], self.saved_coords[mode][i][3]))
        file.close()

    def set_vars(self):
        """
        Adds the gui components
        """
        self.valset.add_float_value('gz', .5, limit='ul', inclusive='', low=0, high=1)
        self.valset.add_int_value('max_iter', 24, limit='l', low=1)
        self.valset.add_float_value('limit', 20.0, limit='l', inclusive='', low=0)
        self.valset.add_complex_value('c', -.25 -.67j)
        self.valset.add_float_value('calctime', 0.0)
        self.valset.add_float_value('flushtime', 0.0)
        self.valset.add_int_value('pal_idx', 0, limit='ul', low=0, high=3)
        self.valset.add_int_value('pal_r', 0)
        self.valset.add_int_value('pal_g', 0)
        self.valset.add_int_value('pal_b', 0)
        self.valset.add_bool_value('mouse_c', False)
        self.valset.add_float_value('saved_gx', 0)
        self.valset.add_float_value('saved_gy', 0)
        self.valset.add_float_value('saved_gw', 0)
        self.valset.add_float_value('saved_gh', 0)

        main = JuliaScreen(0, 200, 500, 500, self.valset, self.valset.get_valobj('gz'))
        self.add_screen('main', main)
        mandel = MandelScreen(250, 200, 250, 500, self.valset, self.valset.get_valobj('gz'))
        mandel.off()
        self.add_screen('mandel', mandel)

        self.add_label('julia_list', 10, 150, 'Julia Set')
        self.add_label('mandel_list', 80, 150, 'Mandelbrot')
        self.add_button('m0b', 10, 130, 50, 15, 'z^2+c', lambda: self.set_mode(0))
        self.add_button('m1b', 80, 130, 50, 15, 'z^2+c', lambda: self.set_mode(1))
        self.add_button('m2b', 10, 110, 50, 15, 'z^3+c', lambda: self.set_mode(2))
        self.add_button('m3b', 80, 110, 50, 15, 'z^3+c', lambda: self.set_mode(3))
        self.add_button('m4b', 10, 90, 50, 15, 'z^1.5+c', lambda: self.set_mode(4))
        self.add_button('m5b', 80, 90, 50, 15, 'z^1.5+c', lambda: self.set_mode(5))
        self.add_button('m6b', 10, 70, 50, 15, 'c*sin(z)', lambda: self.set_mode(6))
        self.add_button('m7b', 10, 50, 120, 15, 'Split z^2+c', lambda: self.set_mode(7))
        self.add_button('resetb', 10, 10, 40, 15, 'Reset(r)', self.reset)
        self.add_toggle_button('mouse_c', 55, 10, 60, 15, 'Mouse C(c)', self.get_valobj('mouse_c'))

        self.add_int_field('max_iter', 150, 180, 120, 15, 'Max Iter', self.get_valobj('max_iter'))
        self.add_float_field('limit', 150, 160, 120, 15, 'Limit', self.get_valobj('limit'))
        self.add_complex_field('c', 150, 140, 120, 15, 'C', self.get_valobj('c'))
        self.add_float_field('zoomfield', 150, 120, 120, 15, 'Zoom Ratio', self.get_valobj('gz'))

        self.add_button('pal_left', 150, 5, 55, 15, 'Idx Left', self.palette_left)
        self.add_button('pal_right', 215, 5, 55, 15, 'Idx Right', self.palette_right)
        self.add_int_slider('pal_r', 150, 70, 120, 15, 0, 'Red  ', self.get_valobj('pal_r'), low=0, high=255)
        self.add_int_slider('pal_g', 150, 50, 120, 15, 0, 'Green', self.get_valobj('pal_g'), low=0, high=255)
        self.add_int_slider('pal_b', 150, 30, 120, 15, 0, 'Blue ', self.get_valobj('pal_b'), low=0, high=255)
        self.add_label('pal_label', 160, 90, 'Palette Index: %i' % self.get_val('pal_idx'))

        self.saved_coords_idx = 0
        self.add_label('saved_coords_idx', 340, 130, 'Saved Coords #%i' % (self.saved_coords_idx + 1))
        self.add_label('saved_coords_c', 340, 115, '   C: ')
        self.add_label('saved_coords_gx', 340, 100, '  GX: ')
        self.add_label('saved_coords_gy', 340, 85, '  GY: ')
        self.add_label('saved_coords_zoom', 340, 70, 'Zoom: ')
        self.add_button('saved_coords_prev', 340, 40, 40, 15, 'Prev(j)', self.saved_coords_prev)
        self.add_button('saved_coords_next', 390, 40, 40, 15, 'Next(k)', self.saved_coords_next)
        self.add_button('saved_coords_goto', 340, 20, 40, 15, 'Goto(g)', self.saved_coords_goto)
        self.add_button('saved_coords_save', 390, 20, 40, 15, 'Save(s)', self.saved_coords_save)
        self.add_button('saved_coords_delete', 440, 20, 60, 15, 'Delete(y)', self.saved_coords_delete)

        self.add_label('leftlabel', 10, 180, '%.5f' % self.get_screen('main').min_gx, color=(255, 0, 255))
        self.add_label('rightlabel', self.width - 60, 180, '%.5f' % self.get_screen('main').max_gx, color=(255, 0, 255))
        self.add_label('toplabel', 10, self.height - 20, '%.5f' % self.get_screen('main').max_gy, color=(255, 0, 255))
        self.add_label('bottomlabel', 10, 210, '%.5f' % self.get_screen('main').min_gy, color=(255, 0, 255))
        self.add_label('zoomlabel', self.width * 3 // 5, 180, 'Zoom: %.5E' % self.get_screen('main').total_zoom)

        self.add_label('calclabel', self.width - 140, 170, '  calc time: %.3f' % self.valset.get_val('calctime'), color=(0, 240, 120))
        self.add_label('flushlabel', self.width - 140, 155, ' flush time: %.3f' % self.valset.get_val('flushtime'), color=(0, 240, 120))

        self.saved_coords = [[],[],[],[],[],[],[]]
        self.load_graph_coords()

    def palette_left(self):
        self.get_valobj('pal_idx').decr()
        self.palette_shift()

    def palette_right(self):
        self.get_valobj('pal_idx').incr()
        self.palette_shift()

    def palette_shift(self):
        self.update_labels()
        pal_idx = self.get_val('pal_idx')
        main = self.get_screen('main')
        self.set_val('pal_r', main.palette[pal_idx][0])
        self.set_val('pal_g', main.palette[pal_idx][1])
        self.set_val('pal_b', main.palette[pal_idx][2])
        self.get_slider('pal_r').update_pos()
        self.get_slider('pal_g').update_pos()
        self.get_slider('pal_b').update_pos()

    def saved_coords_prev(self):
        mode = self.get_screen('main').mode
        if mode in [0, 1, 2, 3, 4, 5, 6]:
            saved_len = len(self.saved_coords[mode])
            if saved_len:
                self.saved_coords_idx -= 1
                if self.saved_coords_idx < 0:
                    self.saved_coords_idx = 0
                self.update_labels()

    def saved_coords_next(self):
        mode = self.get_screen('main').mode
        if mode in [0, 1, 2, 3, 4, 5, 6]:
            saved_len = len(self.saved_coords[mode])
            if saved_len:
                self.saved_coords_idx += 1
                if self.saved_coords_idx >= saved_len:
                    self.saved_coords_idx = saved_len - 1
                self.update_labels()

    def saved_coords_goto(self):
        mode = self.get_screen('main').mode
        if len(self.saved_coords[mode]) == 0:
            return
        if mode in [0, 2, 4, 6]:
            gx, gy, zoom, max_iter, c = self.saved_coords[mode][self.saved_coords_idx]
            main = self.get_screen('main')
            main.set_graph_view(gx, gy, zoom)
            self.set_val('max_iter', max_iter)
            self.set_val('c', c)
            self.render()
        elif mode in [1, 3, 5]:
            gx, gy, zoom, max_iter = self.saved_coords[mode][self.saved_coords_idx]
            main = self.get_screen('main')
            main.set_graph_view(gx, gy, zoom)
            self.set_val('max_iter', max_iter)
            self.render()

    def saved_coords_save(self):
        main = self.get_screen('main')
        mode = main.mode
        if mode in [0, 2, 4, 6]:
            gx, gy, zoom = main.gx, main.gy, main.total_zoom
            max_iter = self.get_val('max_iter')
            c = self.get_val('c')
            self.saved_coords[mode].append([gx, gy, zoom, max_iter, c])
            self.save_graph_coords()
        elif mode in [1, 3, 5]:
            gx, gy, zoom = main.gx, main.gy, main.total_zoom
            max_iter = self.get_val('max_iter')
            self.saved_coords[mode].append([gx, gy, zoom, max_iter])
            self.save_graph_coords()

    def saved_coords_delete(self):
        main = self.get_screen('main')
        mode = main.mode
        if mode in [0, 1, 2, 3, 4, 5, 6]:
            if len(self.saved_coords[mode]):
                print('poppin')
                self.saved_coords[mode].pop(self.saved_coords_idx)
                if self.saved_coords_idx >= len(self.saved_coords[mode]):
                    self.saved_coords_idx = len(self.saved_coords[mode]) - 1
                if self.saved_coords_idx < 0:
                    self.saved_coords_idx = 0

    def reset(self):
        self.screens['main'].reset_screen()
        if self.screens['main'].mode == 7:
            self.screens['mandel'].reset_screen()

    def set_mode(self, mode):
        """
        Sets the mode
        :param mode: mode
        """
        if mode == self.screens['main'].mode:
            return
        if mode in [7, ]:
            self.get_button('saved_coords_goto').off()
            self.get_button('saved_coords_prev').off()
            self.get_button('saved_coords_next').off()
            self.get_button('saved_coords_save').off()
            self.get_button('saved_coords_delete').off()
        else:
            self.get_button('saved_coords_goto').on()
            self.get_button('saved_coords_prev').on()
            self.get_button('saved_coords_next').on()
            self.get_button('saved_coords_save').on()
            self.get_button('saved_coords_delete').on()
        if mode == 7:
            self.screens['mandel'].on()
        else:
            self.screens['mandel'].off()
        self.screens['main'].set_mode(mode)
        self.on_resize(self.width, self.height)
        #self.mouse_up(100, 250, pyglet.window.mouse.RIGHT, None)

    def update_labels(self):
        self.labels['leftlabel'].set_text('%.5f' % self.get_screen('main').min_gx)
        self.labels['rightlabel'].set_text('%.5f' % self.get_screen('main').max_gx)
        self.labels['rightlabel'].set_pos(self.width - 60, 180)
        self.labels['toplabel'].set_text('%.5f' % self.get_screen('main').max_gy)
        self.labels['toplabel'].set_pos(10, self.height - 20)
        self.labels['bottomlabel'].set_text('%.5f' % self.get_screen('main').min_gy)
        self.get_label('zoomlabel').set_pos(self.width * 3 // 5, 180)
        self.get_label('zoomlabel').set_text('Zoom: %.5E' % self.get_screen('main').total_zoom)


        mode = self.get_screen('main').mode
        if mode in [0, 2, 4, 6] and len(self.saved_coords[mode]):
            self.get_label('saved_coords_c').set_text('   C: %.4f+%.4fj' % (self.saved_coords[mode][self.saved_coords_idx][1].real,
                                                                            self.saved_coords[mode][self.saved_coords_idx][1].imag))
        elif mode in [0, 2, 4, 6]:
            self.get_label('saved_coords_c').set_text('   C:')
        else:
            self.get_label('saved_coords_c').set_text('')
        if mode in [0, 1, 2, 3, 4, 5, 6, ] and len(self.saved_coords[mode]):
            self.get_label('saved_coords_gx').set_text('  GX: %.8f' % self.saved_coords[mode][self.saved_coords_idx][0])
            self.get_label('saved_coords_gy').set_text('  GY: %.8f' % self.saved_coords[mode][self.saved_coords_idx][1])
            self.get_label('saved_coords_zoom').set_text('Zoom: %.5E' % self.saved_coords[mode][self.saved_coords_idx][2])
            self.get_label('saved_coords_idx').set_text('Saved Coords #%i' % (self.saved_coords_idx + 1))
        elif mode in [0, 1, 2, 3, 4, 5, 6]:
            self.get_label('saved_coords_gx').set_text('  GX:')
            self.get_label('saved_coords_gy').set_text('  GY:')
            self.get_label('saved_coords_zoom').set_text('Zoom:')
            self.get_label('saved_coords_idx').set_text('Saved Coords #0')
        else:
            self.get_label('saved_coords_gx').set_text('')
            self.get_label('saved_coords_gy').set_text('')
            self.get_label('saved_coords_zoom').set_text('')
            self.get_label('saved_coords_idx').set_text('')


        self.labels['calclabel'].set_text('  calc time: %.3f ms' % self.valset.get_val('calctime'))
        self.labels['calclabel'].set_pos(self.width - 140, 165)
        self.labels['flushlabel'].set_text(' flush time: %.3f ms' % self.valset.get_val('flushtime'))
        self.labels['flushlabel'].set_pos(self.width - 140, 150)

    def mouse_move(self, x, y, dx, dy):
        super().mouse_move(x, y, dx, dy)
        if self.get_val('mouse_c'):
            self.fields['c'].update_label()
            self.screens['main'].render()

    def key_down(self, symbol, modifiers):
        super().key_down(symbol, modifiers)
        if not self.focus:
            main = self.get_screen('main')
            if symbol == pyglet.window.key.C:
                self.get_button('mouse_c').toggle()
            if symbol == pyglet.window.key.R:
                self.reset()
            if self.get_screen('main').mode in [0, 1, 2, 3, 4, 5, 6]:
                if symbol == pyglet.window.key.J:
                    self.saved_coords_prev()
                if symbol == pyglet.window.key.K:
                    self.saved_coords_next()
                if symbol == pyglet.window.key.G:
                    self.saved_coords_goto()
                if symbol == pyglet.window.key.S:
                    self.saved_coords_save()
                if symbol == pyglet.window.key.Y:
                    self.saved_coords_delete()


pyg.run(JuliaWindow, caption='Julia Graph')
