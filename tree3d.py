"""
By Chris Liu

Requires pyglet and pyg to run

How to use:
    2d screen:
        Left click to zoom in.
        Right click to zoom out.
        Arrow keys to move screen.

    3d screen:
        Left/Right, Up/Down, Z/X for rotation.
        A/S for zoom.
        I/J/K/L for translation.

    Click to use buttons.
    Click to select fields, type to enter characters, enter to parse input.
    Click and hold to move sliders.

    Field color:
        Red:
            invalid input
        Blue:
            not within range
        Green:
            accepted

"""


import pyg
from vmath import *
import random


palette = [(155, 87, 18), (196, 103, 9), (224, 137, 31), (143, 224, 31), (89, 216, 30), (25, 186, 16)]


def get_theta(theta):
    """
    Returns a random theta from a gaussian distribution with variance 2.5

    :param theta: theta
    :return: a randomized theta
    """
    ntheta = random.gauss(theta, 2.5)
    if ntheta < theta - 5:
        return theta - 5
    if ntheta > theta + 5:
        return theta + 5
    return ntheta


def get_ratio(ratio):
    """
    Returns a random ratio from a gaussian distribution with variance .04

    :param ratio: ratio
    :return: a randomized ratio
    """
    nratio = random.gauss(ratio, .04)
    if nratio < ratio - .1:
        return ratio - .1
    if nratio > ratio + .1:
        return ratio + .1
    return nratio


def get_branches(branches):
    """
    Returns a random number of branches from a gaussian distribution with variance depending on the average

    :param branches: number of branches
    :return: a randomized number of branches
    """
    nbranches = int(random.gauss(branches + .5, .7 + .25 * (branches - 2)))
    if nbranches < 2:
        return 2
    return nbranches


class Tree2D(pyg.screen.GraphScreen):
    """
    2d screen class.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.iter = 0
        self.theta = 0

    def set_visible(self, visible):
        if not visible:
            self.iter = 0
        super().set_visible(visible)

    def render(self):
        """
        Renders the screen.
        """
        iter = self.get_val('iter')
        theta = self.get_val('theta')
        ratio = self.get_val('ratio')
        branches = self.get_val('branches')
        seeds = []
        if iter:
            self.add_line(*self.on_screen(0, 0), *self.on_screen(0, 4), color=palette[0])
            seeds.append([Vector(0, 4), Vector(0, 4)])
        for i in range(iter):
            if i < 5:
                color = palette[i]
            else:
                color = palette[5]
            new_seeds = []
            for t, v in seeds:
                rtheta1 = get_theta(theta)
                rtheta2 = -get_theta(theta)
                rbranches = get_branches(branches)
                for b in range(rbranches):
                    nv = Vector(*v)
                    btheta = rtheta1 - b * ((rtheta1 - rtheta2) / (rbranches - 1))
                    nv.rotate2d(v_zero(2), btheta)
                    nv *= get_ratio(ratio)
                    self.add_line(*self.on_screen(*t), *self.on_screen(*(t + nv)), color=color)
                    new_seeds.append([t + nv, nv])
            del seeds
            seeds = new_seeds
        del seeds
        self.flush()

    def resize(self, width, height):
        self.refit(width, height - 200)


class Tree3D(pyg.screen.Screen3D):
    """
    3d screen class.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.iter = 0
        self.theta = 0
        self.ratio = 0
        self.branches = 0

    def set_visible(self, visible):
        if not visible:
            self.iter = 0
        super().set_visible(visible)

    def render(self):
        """
        Renders the screen.
        """
        if self.get_val('iter') != self.iter or self.get_val('theta') != self.theta or self.get_val('ratio') != self.ratio or self.get_val('branches') != self.branches:
            #self.add_line(-5000, 0, 0, 5000, 0, 0, color=(255, 0, 0))
            #self.add_line(0, -5000, 0, 0, 5000, 0, color=(0, 255, 0))
            #self.add_line(0, 0, -5000, 0, 0, 5000, color=(0, 0, 255))

            self.add_quad(-200, -200, 0, 200, -200, 0, 200, 200, 0, -200, 200, 0, color=(40, 40, 40))

            iter = self.get_val('iter')
            theta = self.get_val('theta')
            dist = 50
            ratio = self.get_val('ratio')
            branches = self.get_val('branches')
            seeds = []
            d = ~(Vector(0, 0, 1).rotate3d(v_zero(3), v_i(), 0))
            if iter:
                self.add_line(0, 0, 0, *(d * dist), color=palette[0])
                seeds.append((d * dist, d * dist))
            for i in range(0, iter):
                if i < 5:
                    color = palette[i]
                else:
                    color = palette[5]
                new_seeds = []
                for t, v in seeds:
                    rbranches = get_branches(branches)
                    theta1 = random.random() * 360
                    for b in range(rbranches):
                        nv = Vector(*v)
                        rtheta = get_theta(theta)
                        axis2d = Vector(1, 0).rotate2d(v_zero(2), theta1 + b * 360 / branches)
                        axis = Vector(*axis2d, 0)
                        nv.rotate3d(v_zero(3), axis, rtheta)
                        nv *= get_ratio(ratio)
                        self.add_line(*t, *(t + nv), color=color)
                        new_seeds.append([t + nv, nv])
                del seeds
                seeds = new_seeds
            del seeds

            self.flush()
            self.iter = iter
            self.theta = theta
            self.ratio = ratio
            self.branches = branches

    def resize(self, width, height):
        self.w = width
        self.h = height - 200


class Test3D(pyg.window.Window):
    def set_vars(self):
        self.is3d = False

        self.add_float_value('gz', .5, limit='ul', inclusive='')
        self.add_int_value('iter', 1, limit='ul', low=0, high=10)
        self.add_float_value('theta', 25.0, limit='ul', low=5, high=55)
        self.add_float_value('ratio', .75, limit='ul', low=.4, high=.9)
        self.add_int_value('branches', 2, limit='ul', low=1, high=6)

        self.add_int_field('iter', 100, 100, 120, 15, 'Iter', self.get_valobj('iter'))
        self.add_float_field('theta', 100, 80, 120, 15, 'Theta', self.get_valobj('theta'))
        self.add_float_field('ratio', 100, 60, 120, 15, 'Ratio', self.get_valobj('ratio'))
        self.add_int_field('branches', 100, 40, 120, 15, 'Branches', self.get_valobj('branches'))

        tree2d = Tree2D(0, 200, 500, 500, 0, 5, 10, 10, self.valset, self.get_valobj('gz'))
        self.add_screen('2d', tree2d)
        tree3d = Tree3D(0, 200, 500, 500, Vector(0, 0, -200), Vector(-75, 0, 45), v_zero(3), self.valset, bg=(255, 255, 255))
        tree3d.off()
        self.add_screen('3d', tree3d)

        self.add_button('switch', 20, 20, 40, 40, 'Switch', self.switch)
        self.add_button('redraw', 260, 20, 40, 40, 'Redraw', self.redraw)
        self.get_button('redraw').off()

    def switch(self):
        """
        Switches between the 2d and 3d screens.
        """
        if not self.is3d:
            self.get_screen('2d').off()
            self.get_screen('3d').on()
        else:
            self.get_screen('3d').off()
            self.get_screen('2d').on()
        self.is3d = not self.is3d

    def redraw(self):
        """
        Redraws the 3d screen.
        """
        self.get_screen('3d').iter = 0
        self.render()

if __name__ == '__main__':
    pyg.run(Test3D, caption='Fractal Tree')
