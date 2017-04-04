"""
Left click to zoom in.
Right click to zoom out.
Arrow keys to move screen.

Click the E buttons to edit corresponding transformation.
"""

import pyg

import numpy as np
from numba import jit, guvectorize

from math import cos, sin, pi
import time


class Transform:
    def __init__(self, arr, string, shortstring, *args):
        self.arr = arr
        self.string = string
        self.shortstring = shortstring
        self.args = args


def m_trans(x, y):
    return Transform(np.array([[1, 0, x],
                               [0, 1, y],
                               [0, 0, 1]]),
                     'Translate(%s, %s)' % tuple(map(lambda x: str(round(x, 5)), (x, y))),
                     'T(%s, %s)' % tuple(map(lambda x: str(round(x, 2)), (x, y))),
                     x, y)


def m_scale(w, h):
    return Transform(np.array([[w, 0, 0],
                               [0, h, 0],
                               [0, 0, 1]]),
                     'Scale(%s, %s)' % tuple(map(lambda x: str(round(x, 5)), (w, h))),
                     'S(%s, %s)' % tuple(map(lambda x: str(round(x, 2)), (w, h))),
                     w, h)


def m_rotate(theta):
    t = theta * pi / 180.0
    return Transform(np.array([[ cos(t), -sin(t),  0],
                               [ sin(t),  cos(t),  0],
                               [      0,       0,  1]]),
                     'Rotate(%s)' % str(round(theta, 3)),
                     'R(%s)' % str(round(theta, 3)),
                     theta)


def m_rotate2(theta1, theta2):
    t1 = theta1 * pi / 180.0
    t2 = theta2 * pi / 180.0
    return Transform(np.array([[ cos(t1), -sin(t2),  0],
                               [ sin(t1),  cos(t2),  0],
                               [      0,       0,  1]]),
                     '',
                     '',
                     theta1, theta2)


@guvectorize('(float64[:], float64[:,:,:], int32[:], int32[:], int32[:], float64[:])', '(n),(r,s,s),(t),(),(),(m)', target='parallel')
def get_points_vec_parallel(point, t, p, trans, it, output):
    trans = trans[0]
    it = it[0]
    psize = p.shape[0]
    tmpp = np.empty(3)
    for i in range(trans):
        k = p[np.random.randint(psize)]
        tmpp[:] = point
        for j in range(3):
            point[j] = t[k][j][0] * tmpp[0] + t[k][j][1] * tmpp[1] + t[k][j][2] * tmpp[2]
    for i in range(it):
        k = p[np.random.randint(psize)]
        tmpp[:] = point
        for j in range(3):
            point[j] = t[k][j][0] * tmpp[0] + t[k][j][1] * tmpp[1] + t[k][j][2] * tmpp[2]
        idx = i * 3
        output[idx] = point[0]
        output[idx + 1] = point[1]
        output[idx + 2] = 1


@jit
def get_points(npoints, t, p, trans, it):
    startpoints = np.column_stack((np.random.uniform(-10, 10, npoints), np.random.uniform(-10, 10, npoints), np.ones(npoints)))
    output = np.empty((npoints, it * 3), dtype=np.float)
    get_points_vec_parallel(startpoints, t, p, trans, it, output)
    return output


class TransformationScreen(pyg.screen.GraphScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rendered = False
        self.t_list = []
        self.p_list = []

        #self.load_alphabet()

        self.t_list.append([m_scale(.5, .5)])
        self.t_list.append([m_scale(.5, .5), m_trans(2.5, 5)])
        self.t_list.append([m_scale(.5, .5), m_trans(5, 0)])
        self.p_list = [3, 1, 1]

    '''
    def load_alphabet(self):
        file = open('alphabet', 'r')
        line = file.readline()
        while line:
            linargs = line.split(' ')
            args = []
            for arg in linargs:
                if arg:
                    args.append(float(arg))
            tf = []
            tf.append(m_trans(args[4], args[5]))
            tf.append(m_scale(args[8], args[9]))
            tf.append(m_rotate2(args[10], args[11]))
            self.t_list.append(tf)
            self.p_list.append(int(10000 * args[6]))
            line = file.readline()
    '''

    def render(self):
        if not self.rendered:
            if not self.t_list:
                self.rendered = True
                self.flush()
                return

            tf_list = []
            for tp_list in self.t_list:
                tf = np.eye(3)
                for tp in tp_list:
                    tf = tp.arr @ tf
                tf_list.append(tf)
            t = np.array(tf_list)
            p = np.array([i for i in range(len(self.p_list)) for _ in range(self.p_list[i])], dtype=np.int32)

            trans = self.get_val('trans')
            it = self.get_val('iter')
            npoints = self.get_val('points')

            start2 = time.time()
            points = get_points(npoints, t, p, trans, it).flatten()
            end2 = time.time()
            colors = np.zeros(len(points), dtype=np.int)
            self.set_points(points, colors)

            start = time.time()
            self.flush()
            end = time.time()

            self.rendered = True

            self.set_val('flushtime', ((end - start) * 1000))
            self.set_val('calctime', ((end2 - start2) * 1000))

    def resize(self, width, height):
        self.refit(width, height - 250)


class TransformationWindow(pyg.window.Window):
    def reset(self):
        self.screens['main'].t_list.clear()
        self.screens['main'].p_list.clear()
        self.current_part = -1
        self.current_transform = -1
        self.redraw()

    def set_vars(self):
        self.add_float_value('gz', .5, limit='ul', inclusive='', low=0, high=1)
        self.add_screen('main', TransformationScreen(0, 250, 800, 500, 5, 5, 10 * 8 / 5, 10, self.valset, self.get_valobj('gz')))
        self.add_button('resetscreen', 10, 80, 40, 30, 'Reset\nScreen', self.get_screen('main').reset_screen)
        self.add_button('redraw', 60, 80, 40, 30, 'Redraw\nScreen', self.redraw)
        self.add_button('reset', 10, 10, 40, 30, 'Reset\nSystem', self.reset)

        self.add_int_value('trans', 100, limit='l', low=0)
        self.add_int_value('iter', 100, limit='l', low=0)
        self.add_int_value('points', 1000, limit='l', low=0)

        self.add_int_field('trans', 10, 225, 100, 15, 'Trans', self.get_valobj('trans'))
        self.add_int_field('iter', 10, 205, 100, 15, 'Iter', self.get_valobj('iter'))
        self.add_int_field('points', 10, 185, 100, 15, 'Points', self.get_valobj('points'))

        self.add_float_value('flushtime')
        self.add_float_value('calctime')
        self.add_label('flushtime', color=(255, 0, 255))
        self.add_label('calctime', color=(255, 0, 255))

        # states
        # -2: new, -1: none, 0...: index
        # no -2 for current_transform
        self.current_part = -1
        self.current_transform = -1

        # labelrows
        self.add_label_row('transformparts', 120, 135, 300, 100, 45, 5, self.get_transform_parts)
        self.add_button('tp0', 425, 220, 15, 15, 'E', lambda: self.load_tp(0))
        self.add_button('tp1', 425, 200, 15, 15, 'E', lambda: self.load_tp(1))
        self.add_button('tp2', 425, 180, 15, 15, 'E', lambda: self.load_tp(2))
        self.add_button('tp3', 425, 160, 15, 15, 'E', lambda: self.load_tp(3))
        self.add_button('tp4', 425, 140, 15, 15, 'E', lambda: self.load_tp(4))

        self.add_label_row('transformall', 460, 135, 300, 100, 45, 5, self.get_transform_all)
        self.add_button('ta0', 765, 220, 15, 15, 'E', lambda: self.load_ta(0))
        self.add_button('ta1', 765, 200, 15, 15, 'E', lambda: self.load_ta(1))
        self.add_button('ta2', 765, 180, 15, 15, 'E', lambda: self.load_ta(2))
        self.add_button('ta3', 765, 160, 15, 15, 'E', lambda: self.load_ta(3))
        self.add_button('ta4', 765, 140, 15, 15, 'E', lambda: self.load_ta(4))

        self.add_label('parttitle', 250, 240, 'Transforms')
        self.add_label('alltitle', 590, 240, 'System')

        self.add_float_value('x')
        self.add_float_value('y')
        self.add_float_field('x', 120, 100, 90, 15, 'x', self.get_valobj('x'))
        self.add_float_field('y', 120, 80, 90, 15, 'y', self.get_valobj('y'))
        self.add_button('save_transform', 150, 60, 30, 15, 'Save', self.save_transform)
        self.fields['x'].off()
        self.fields['y'].off()
        self.buttons['save_transform'].off()

        self.add_float_value('w')
        self.add_float_value('h')
        self.add_float_field('w', 220, 100, 90, 15, 'w', self.get_valobj('w'))
        self.add_float_field('h', 220, 80, 90, 15, 'h', self.get_valobj('h'))
        self.add_button('save_scale', 250, 60, 30, 15, 'Save', self.save_scale)
        self.fields['w'].off()
        self.fields['h'].off()
        self.buttons['save_scale'].off()

        self.add_float_value('theta')
        self.add_float_field('theta', 320, 100, 90, 15, 'theta', self.get_valobj('theta'))
        self.add_button('save_rotate', 350, 60, 30, 15, 'Save', self.save_rotate)
        self.fields['theta'].off()
        self.buttons['save_rotate'].off()

        self.add_int_value('index', limit='ul', low=0, high=0)
        self.add_int_field('index', 120, 10, 60, 15, 'index', self.get_valobj('index'))
        self.fields['index'].off()

        self.add_button('new_part', 150, 30, 30, 15, 'New', self.new_part)
        self.add_button('delete_part', 250, 30, 40, 15, 'Delete', self.delete_part)
        self.add_button('cancel_part', 350, 30, 40, 15, 'Cancel', self.cancel_part)
        self.buttons['delete_part'].off()
        self.buttons['cancel_part'].off()

        self.add_int_value('p', limit='l', low=0)
        self.add_int_field('p', 460, 100, 60, 15, 'p', self.get_valobj('p'))
        self.add_button('save_p', 460, 60, 30, 15, 'Save', self.save_p)
        self.fields['p'].off()
        self.buttons['save_p'].off()

        self.add_button('new_transform', 460, 30, 30, 15, 'New', self.new_transform)
        self.add_button('delete_transform', 560, 30, 40, 15, 'Delete', self.delete_transform)
        self.add_button('cancel_transform', 660, 30, 40, 15, 'Cancel', self.cancel_transform)
        self.buttons['delete_transform'].off()
        self.buttons['cancel_transform'].off()

        self.add_label('current_part', 220, 120)
        self.add_label('current_transform', 600, 120)

        self.add_label('focus', color=(255, 0, 255))
        self.add_label('hover', color=(255, 0, 255))

    def update_labels(self):
        self.labels['flushtime'].set_text('flush time: %.5fms' % self.get_val('flushtime'))
        self.labels['flushtime'].set_pos(self.width - 150, 100)
        self.labels['calctime'].set_text(' calc time: %.5fms' % self.get_val('calctime'))
        self.labels['calctime'].set_pos(self.width - 150, 90)

        if self.current_part >= 0:
            self.labels['current_part'].set_text('Transform Part %d' % self.current_part)
        elif self.current_part == -2:
            self.labels['current_part'].set_text('New Transform Part')
        else:
            self.labels['current_part'].set_text('')

        if self.current_transform >= 0:
            self.labels['current_transform'].set_text('Transform %d' % self.current_transform)
        else:
            self.labels['current_transform'].set_text('')

        self.labels['focus'].set_pos(self.width - 150, 80)
        if self.focus:
            self.labels['focus'].set_text(str(self.focus.__class__))
        else:
            self.labels['focus'].set_text('')

        self.labels['hover'].set_pos(self.width - 150, 70)
        if self.hover:
            self.labels['hover'].set_text(str(self.hover.__class__))
        else:
            self.labels['hover'].set_text('')

    def get_transform_parts(self):
        if self.current_transform >= 0:
            t_list = self.screens['main'].t_list
            output = []
            tp_list = t_list[self.current_transform]
            for i, tp in enumerate(tp_list):
                output.append(str(i) + ' | ' + tp.string)
            return output
        else:
            return []

    def get_transform_all(self):
        t_list = self.screens['main'].t_list
        p_list = self.screens['main'].p_list
        if t_list:
            output = []
            for i, tp_list in enumerate(t_list):
                tstring = '%d | P(%d) ' % (i, p_list[i])
                for tp in tp_list:
                    tstring += tp.shortstring + ' '
                output.append(tstring)
            return output
        else:
            return []

    def load_tp(self, i):
        if self.current_transform < 0:
            return
        if self.current_part == -1:
            t_list = self.screens['main'].t_list
            if not t_list:
                return
            i = self.get_val('transformparts__intvalue') + i
            tp_list = t_list[self.current_transform]
            if i < len(tp_list):
                self.current_part = i

                ttype = tp_list[self.current_part].string[0]
                if ttype == 'T':
                    self.set_val('x', tp_list[self.current_part].args[0])
                    self.set_val('y', tp_list[self.current_part].args[1])
                elif ttype == 'S':
                    self.set_val('w', tp_list[self.current_part].args[0])
                    self.set_val('h', tp_list[self.current_part].args[1])
                else:
                    self.set_val('theta', tp_list[self.current_part].args[0])

                self.parts_on()
        else:
            self.parts_off()
            self.current_part = -1
            self.load_tp(i)

    def save_transform(self):
        t_list = self.screens['main'].t_list
        if self.current_part >= 0:
            t_list[self.current_transform][self.current_part] = m_trans(self.get_val('x'), self.get_val('y'))
        else:
            t_list[self.current_transform].insert(self.get_val('index'), m_trans(self.get_val('x'), self.get_val('y')))
        self.parts_off()
        self.current_part = -1
        self.labelrows['transformparts'].render()
        self.labelrows['transformall'].render()

    def save_scale(self):
        t_list = self.screens['main'].t_list
        if self.current_part >= 0:
            t_list[self.current_transform][self.current_part] = m_scale(self.get_val('w'), self.get_val('h'))
        else:
            t_list[self.current_transform].insert(self.get_val('index'), m_scale(self.get_val('w'), self.get_val('h')))
        self.parts_off()
        self.current_part = -1
        self.labelrows['transformparts'].render()
        self.labelrows['transformall'].render()

    def save_rotate(self):
        t_list = self.screens['main'].t_list
        if self.current_part >= 0:
            t_list[self.current_transform][self.current_part] = m_rotate(self.get_val('theta'))
        else:
            t_list[self.current_transform].insert(self.get_val('index'), m_rotate(self.get_val('theta')))
        self.parts_off()
        self.current_part = -1
        self.labelrows['transformparts'].render()
        self.labelrows['transformall'].render()

    def new_part(self):
        if self.current_transform < 0 or self.current_part == -2:
            return
        if self.current_part >= 0:
            self.parts_off()
        self.current_part = -2
        self.get_valobj('index').high = len(self.screens['main'].t_list[self.current_transform])
        self.set_val('index', len(self.screens['main'].t_list[self.current_transform]))
        self.parts_on()

    def delete_part(self):
        t_list = self.screens['main'].t_list
        t_list[self.current_transform].pop(self.current_part)
        self.parts_off()
        self.current_part = -1
        self.labelrows['transformparts'].render()
        self.labelrows['transformall'].render()

    def cancel_part(self):
        self.parts_off()
        self.current_part = -1

    def parts_on(self):
        fields = ['x', 'y', 'w', 'h', 'theta']
        if self.current_part == -2:
            fields.append('index')
        for f in fields:
            self.fields[f].on()
        buttons = ['save_transform', 'save_scale', 'save_rotate', 'delete_part', 'cancel_part']
        if self.current_part == -2:
            buttons.remove('delete_part')
        for b in buttons:
            self.buttons[b].on()

    def parts_off(self):
        fields = ['x', 'y', 'w', 'h', 'theta']
        if self.current_part == -2:
            fields.append('index')
        for f in fields:
            self.set_val(f, 0)
            self.fields[f].off()
        buttons = ['save_transform', 'save_scale', 'save_rotate', 'delete_part', 'cancel_part']
        for b in buttons:
            self.buttons[b].off()

    def load_ta(self, i):
        if self.current_transform == -1:
            t_list = self.screens['main'].t_list
            if not t_list:
                return
            i = self.sliders['transformall__intvslider'].valobj.value + i
            if i < len(t_list):
                self.current_transform = i

                self.set_val('p', int(self.screens['main'].p_list[self.current_transform]))
                self.all_on()

            self.labelrows['transformparts'].render()
        else:
            self.current_transform = -1
            self.all_off()
            self.load_ta(i)

    def save_p(self):
        p_list = self.screens['main'].p_list
        p_list[self.current_transform] = self.get_val('p')
        self.labelrows['transformall'].render()

    def new_transform(self):
        self.screens['main'].t_list.append([])
        self.screens['main'].p_list.append(1)
        self.labelrows['transformall'].render()
        self.set_val('transformall__intvalue', self.get_valobj('transformall__intvalue').high)
        self.labelrows['transformall'].render()
        if self.get_val('transformall__intvalue') > 0:
            self.load_ta(4)
        else:
            self.load_ta(len(self.screens['main'].t_list) - 1)

    def delete_transform(self):
        t_list = self.screens['main'].t_list
        t_list.pop(self.current_transform)
        p_list = self.screens['main'].p_list
        p_list.pop(self.current_transform)
        self.parts_off()
        self.all_off()
        self.current_part = -1
        self.current_transform = -1
        self.labelrows['transformparts'].render()
        self.labelrows['transformall'].render()

    def cancel_transform(self):
        self.parts_off()
        self.all_off()
        self.current_part = -1
        self.current_transform = -1
        self.labelrows['transformparts'].render()

    def all_on(self):
        fields = ['p']
        for f in fields:
            self.fields[f].on()
        buttons = ['save_p', 'delete_transform', 'cancel_transform']
        for b in buttons:
            self.buttons[b].on()

    def all_off(self):
        fields = ['p']
        for f in fields:
            self.fields[f].off()
        buttons = ['save_p', 'delete_transform', 'cancel_transform']
        for b in buttons:
            self.buttons[b].off()

    def redraw(self):
        self.get_screen('main').rendered = False
        self.render()


if __name__ == '__main__':
    pyg.run(TransformationWindow, width=800, height=750, caption='Transformations')
