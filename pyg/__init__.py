"""
A graphics package using pyglet.

ORDERED GROUPS:
1: buttons
2: labels

TODO:
finish documentation.
status line at bottom?
let opengl do graphscreen zoom? test speeds
move required functions into on_(action), change overridden functions to (action)
Remove visible from constructors. ??? why ???
3dscreen: maximum zoom conflict with background
make gui, screen, valset, and window modules
make sure mouse coordinates are consistent
"""


__author__ = 'Christopher Liu'


from . import gui
from . import screen
from . import valset
from . import window


def run(WindowCls, width=500, height=700, caption='Caption Here', ticktime=0):
    """
    Runs pyglet using a provided Window subclass.

    :type WindowCls: Window
    :param WindowCls: a subclass of Window
    :type width: int
    :param width: width
    :type height: int
    :param height: height
    :type caption: str
    :param caption: caption
    :type ticktime: float
    :param ticktime: interval between ticks in seconds, zero to disable ticking
    """
    WindowCls(width=width, height=height, caption=caption, bg=(0, 0, 0, 1), ticktime=ticktime, resizable=True)
    import pyglet
    pyglet.app.run()
