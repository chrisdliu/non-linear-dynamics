import pyg
from vmath import *
from random import random


class Screen3D(pyg.screen.Screen3D):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.iter = 0

    def render(self):
        if self.get_val('iter') != self.iter:
            self.add_line(-5000, 0, 0, 5000, 0, 0, color=(255, 0, 0))
            self.add_line(0, -5000, 0, 0, 5000, 0, color=(0, 255, 0))
            #self.add_line(0, 0, -5000, 0, 0, 5000, color=(0, 0, 255))

            iter = self.get_val('iter')
            dist = 100
            ratio = 3/4
            seeds = []
            if iter:
                self.add_line(0, 0, 0, 0, 0, dist)
                seeds.append((Vector(0, 0, dist), v_k))
            for i in range(0, iter):
                dist *= ratio
                new_seeds = []
                for v, d in seeds:
                    v1 = d * dist
                    v1.rotate(v_zero(3), v_i, -30 + 10 * random() - 2)
                    d1 = ~v1
                    v1 += v
                    self.add_line(*v, *v1)
                    new_seeds.append((v1, d1))
                    v2 = d * dist
                    v2.rotate(v_zero(3), ~Vector(-1, 3 ** .5, 0), -30 + 10 * random() - 2)
                    d2 = ~v2
                    v2 += v
                    self.add_line(*v, *v2)
                    new_seeds.append((v2, d2))
                    v3 = d * dist
                    v3.rotate(v_zero(3), ~Vector(-1, -(3 ** .5), 0), -30 + 10 * random() - 2)
                    d3 = ~v3
                    v3 += v
                    self.add_line(*v, *v3)
                    new_seeds.append((v3, d3))
                del seeds
                seeds = new_seeds
            del seeds

            self.flush()
            self.iter = iter

    def resize(self, width, height):
        self.w = width
        self.h = height - 200


class Test3D(pyg.window.Window):
    def set_vars(self):
        self.add_int_value('iter', 1, limit='ul', low=0, high=10)
        self.add_int_field('iter', 100, 100, 120, 15, 'Iter', self.get_valobj('iter'))
        self.add_screen('main', Screen3D(0, 200, 500, 500, Vector(0, 0, -400), v_zero(3), v_zero(3), self.valset))


pyg.run(Test3D)