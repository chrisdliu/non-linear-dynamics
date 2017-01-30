"""
A graphics module using pyglet

ORDERED GROUPS:
window:
 1: buttons
 2: labels

TODO:
status line at bottom?
let opengl do graphscreen zoom? test speeds
fix gui obj inheritance tree
"""


__author__ = 'Christopher Liu'


from . import screen
from . import window


def run(WindowCls, width=500, height=700, caption='Caption Here'):
    WindowCls(width=width, height=height, caption=caption, bg=(0, 0, 0, 1), resizable=True)
    import pyglet
    pyglet.app.run()
