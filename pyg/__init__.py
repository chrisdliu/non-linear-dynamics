"""
By Chris Liu

A graphics module using pyglet

ORDERED GROUPS:
window:
 1: buttons
 2: labels

TODO:
status line at bottom?
Let opengl do graphscreen zoom? test speeds
"""


from .gui import *
from .screen import *
from .valset import *
from .window import *


def run(WindowCls, width=500, height=700, caption='Caption Here'):
    WindowCls(width=width, height=height, caption=caption, bg=(0, 0, 0, 1), resizable=True)
    pyglet.app.run()
