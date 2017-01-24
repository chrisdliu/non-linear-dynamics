"""
By Chris Liu

A module for using pyglet

ORDERED GROUPS:
window:
 0: buttons
 1: labels
screen:
-1: background
 0: stuff

TODO:
status line at bottom?
"""


from .gui import *
from .screen import *
from .valset import *
from .window import *


def run(WindowCls, width=500, height=700, caption='Caption Here'):
    window = WindowCls(width=width, height=height, caption=caption, bg=(0, 0, 0, 1), resizable=True)
    pyglet.app.run()
