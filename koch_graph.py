"""
Requires pyglet, numpy, and pyg to run

How to use:
Left click to zoom in
Right click to zoom out
Arrow keys to move screen
Click to use buttons
Click to select fields, type to enter characters, enter to parse input
Click and hold to move sliders
"""

import pyg
import pyglet
import math
import numpy as np


def get_line_points(line_points, theta, maxlevel, level=0):
    """
    Recursive program that returns an array of line strip points for the koch curve
    :param line_points: array of line strip points
    :param theta: koch angle
    :param maxlevel: max koch level
    :param level: current level
    :return: array of line strip points
    """
    if level == maxlevel:
        return line_points
    next_line_points = np.empty((4 ** (level + 1) + 1) * 2)
    for i in range(line_points.shape[0] // 2)[:-1]:
        sx = line_points[i * 2]
        sy = line_points[i * 2 + 1]
        ex = line_points[i * 2 + 2]
        ey = line_points[i * 2 + 3]
        dx = ex - sx
        dy = ey - sy
        angle = math.atan2(dy, dx)
        dist = math.sqrt(dx * dx + dy * dy)
        new_dist = 1 / (2 * (math.cos(theta) + 1)) * dist

        next_line_points[i * 8] = sx
        next_line_points[i * 8 + 1] = sy

        nx = sx + new_dist * math.cos(angle)
        ny = sy + new_dist * math.sin(angle)
        next_line_points[i * 8 + 2] = nx
        next_line_points[i * 8 + 3] = ny
        nx += new_dist * math.cos(theta + angle)
        ny += new_dist * math.sin(theta + angle)
        next_line_points[i * 8 + 4] = nx
        next_line_points[i * 8 + 5] = ny
        nx += new_dist * math.cos(angle - theta)
        ny += new_dist * math.sin(angle - theta)
        next_line_points[i * 8 + 6] = nx
        next_line_points[i * 8 + 7] = ny
        nx += new_dist * math.cos(angle)
        ny += new_dist * math.sin(angle)

    next_line_points[-2] = line_points[-2]
    next_line_points[-1] = line_points[-1]
    return get_line_points(next_line_points, theta, maxlevel, level + 1)


class koch_screen(pyg.screen.GraphScreen):
    def __init__(self, x, y, width, height, valset, zoom_valobj, bg=(255, 255, 255), visible=True):
        super().__init__(x, y, width, height, 2.5, 2.5, 5, 5, valset, zoom_valobj, bg=bg, visible=visible)

    def render(self):
        theta = self.get_val('theta') * math.pi / 180
        if (self.get_val('theta') + 180) % 360 == 0:
            self.set_val('lines', 0)
            self.set_val('simdim', 0)
            self.set_val('length', 0)
        else:
            plist = get_line_points(np.array([*self.on_screen(1, 1), *self.on_screen(4, 1)]), theta, self.get_val('level'))
            clist = np.zeros(len(plist) * 3 // 2, dtype=np.ubyte)
            self.set_line_strip(plist, clist)
            self.set_val('lines', len(plist) // 2 - 1)
            self.set_val('simdim', math.log(4) / (math.log(2) + math.log(1 + abs(math.cos(theta)))))
            self.set_val('length', (4 / (2 * (1 + math.cos(theta)))) ** self.get_val('level'))
        self.flush()

    def resize(self, width, height):
        self.refit(width, height - 200)


def get_length_text(length):
    """
    Returns the length in more meaningful measurements
    :param length: length
    :return: a string
    """
    if length < 10 ** 2:
        return '%.5f meters' % length
    elif length < 10 ** 4:
        return '%.5f football fields' % (length / 109.7)
    elif length < 10 ** 6:
        return '%.5f central parks' % (length / 4000)
    elif length < 10 ** 8:
        return '%.5f californias' % (length / 1200000)
    elif length < 10 ** 10:
        return '%.5f trips from the earth to the moon' % (length / 380000000)
    else:
        return '%.5f AUs' % (length / 150000000000)


class koch_window(pyg._window.Window):
    def set_vars(self):
        #ds = (log 4) / (log 2 + log (1 + cos(theta)))
        self.valset.add_float_value('gz', .5, limit='ul', inclusive='', low=0, high=1)
        self.valset.add_int_value('level', 0, limit='ul', low=0, high=9)
        self.valset.add_float_value('theta', 60)

        self.valset.add_int_value('lines', 1)
        self.valset.add_float_value('simdim', 1)
        self.valset.add_float_value('length', 1)

        main = koch_screen(0, 200, 500, 500, self.valset, self.get_valobj('gz'))
        self.add_screen('main', main)

        self.add_float_field('zoomfield', 100, 130, 120, 15, 'Zoom Ratio', self.get_valobj('gz'))
        self.add_int_field('levelfield', 100, 100, 120, 15, 'Level', self.get_valobj('level'))
        self.add_float_field('thetafield', 100, 70, 120, 15, 'Theta', self.get_valobj('theta'))

        self.add_button('resetb', 10, 10, 40, 40, 'Reset', self.get_screen('main').reset_screen)

        self.add_label('lines_label', 300, 100, color=(255, 0, 255))
        self.add_label('simdim_label', 300, 80, color=(255, 0, 255))
        self.add_label('length_label', 300, 60, color=(255, 0, 255))

    def update_labels(self):
        self.get_label('lines_label').set_text('Lines: %d' % self.get_val('lines'))
        self.get_label('simdim_label').set_text('Dimension: %.5f' % self.get_val('simdim'))
        self.get_label('length_label').set_text(get_length_text(self.get_val('length')))


window = koch_window(width=500, height=700, caption='Koch Graph', bg=(0, 0, 0, 1), resizable=True)
pyglet.app.run()
