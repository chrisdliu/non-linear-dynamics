"""
A graphics package using pyglet.

Install pyglet from bitbucket to fix stupid event loop

TODO:
finish documentation.
status line at bottom?
move required functions into on_(action), change overridden functions to (action)
Remove visible from constructors. ??? why ???
3dscreen: maximum zoom conflict with background
make sure mouse coordinates are consistent
add generic slider superclass
look over click logic
button hover while clicked
resize vertex_list vs creating new one?
add updatefunc to sliders
is there any point of having focusable
redo focus logic for more modularity

add parent and batch as first arguments
pass all valobjs by string
"""


__author__ = 'Christopher Liu'


from . import gui
from . import screen
from . import valset
from . import window


def run(WindowCls, width, height, caption='Caption Here', bg=(0, 0, 0), ticktime=0):
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
    WindowCls(width=width, height=height, caption=caption, bg=bg, ticktime=ticktime, resizable=True)
    import pyglet
    pyglet.app.run()
