"""
Defines gui objects (GuiObj) and gui components (GuiComp).
"""

import pyglet.gl as _gl
import pyglet.graphics as _graphics
import pyglet.text as _text
import pyglet.window as _win

from pyg.valset import *


def rdim(x, y, w, h):
    return x, y, x + w, y, x + w, y + h, x, y + h


class GuiObject:
    """
    Basic gui object class (labels, guicomponents).

    :ivar x: x coord
    :ivar y: y coord
    :ivar w: width
    :ivar h: height
    :ivar visible: if the gui object is drawn
    """

    og0 = _graphics.OrderedGroup(0)
    og1 = _graphics.OrderedGroup(1)
    og2 = _graphics.OrderedGroup(2)

    def __init__(self, parent, name, x, y, width, height, visible=True):
        """
        Gui object constructor.

        :type x: float
        :param x: x coord
        :type y: float
        :param y: y coord
        :type width: float
        :param width: width
        :type height: float
        :param height: height
        :type batch: pyglet.graphics.Batch
        :param batch: the window's batch
        :type visible: bool
        :param visible: if the gui object is drawn
        """
        self.parent = parent
        self._batch = parent._batch
        self.name = name
        self.x = x
        self.y = y
        self.w = width
        self.h = height
        self.visible = visible

    def set_pos(self, x, y):
        """
        Sets the gui object's position

        :type x: int
        :param x: x
        :type y: int
        :param y: y
        """
        self.x = x
        self.y = y

    def set_size(self, width, height):
        """
        Sets the gui object's dimensions

        :param int width: width
        :param int height: height
        :return:
        """
        self.w = width
        self.h = height

    def set_visible(self, visible):
        """
        Sets the gui object's visible attribute.
        If True, renders the gui object.
        If False, unrenders the gui object.

        :type visible: bool
        :param visible: visible
        """
        self.visible = visible
        if visible:
            self.render()

    def on(self):
        """
        Sets visible to True
        """
        self.set_visible(True)

    def off(self):
        """
        Sets visible to False
        """
        self.set_visible(False)

    def render(self):
        """
        Renders the gui object.
        Should clear and re-add its vertex lists.
        Should be overridden.
        """
        pass


class Label(GuiObject):
    """
    A label class (text).

    :ivar x: x coord
    :ivar y: y coord
    :ivar text: text
    :ivar color: color
    :ivar visible: if the label is drawn
    """

    def __init__(self, parent, name, x, y, text, color=(255, 255, 255), visible=True, **kwargs):
        """
        Label constructor.

        :type x: float
        :param x: x coord
        :type y: float
        :param y: y coord
        :type text: str
        :param text: text
        :type batch: pyglet.graphics.Batch
        :param batch: the window's batch
        :type color: list(int * 3)
        :param color: color
        """
        super().__init__(parent, name, x, y, 0, 0, visible)
        self.text = text
        self._pyglet_label = _text.Label(text, font_name='Menlo', font_size=8, x=x, y=y, batch=parent._batch,
                                         group=self.og2, color=(*color, 255), **kwargs)
        self.set_visible(visible)

    def set_pos(self, x, y):
        super().set_pos(x, y)
        self._pyglet_label.x = x
        self._pyglet_label.y = y

    def set_visible(self, visible):
        if visible:
            self._pyglet_label.text = self.text
        else:
            self._pyglet_label.text = ''
        self.visible = visible

    def set_text(self, text):
        """
        Sets the label's text.

        :type text: str
        :param text: text
        """
        self.text = text
        self.set_visible(self.visible)


class GuiComponent(GuiObject):
    """
    Base gui component (buttons, fields, sliders) class.

    :ivar x: x coord
    :ivar y: y coord
    :ivar w: width
    :ivar h: height
    :ivar visible: if the component is drawn
    :ivar focusable: if the component can be in focus
    :ivar is_focus: if the component is in focus
    :ivar is_hover: if the mouse is hovering over the component
    """

    _vertex_types = ('quads',)

    def __init__(self, parent, name, x, y, width, height, focusable=False, visible=True, interfaced=False):
        """
        Gui component constructor.

        :type x: int
        :param x: x coord
        :type y: int
        :param y: y coord
        :type width: int
        :param width: width
        :type height: int
        :param height: height
        :type batch: pyglet.graphics.Batch
        :param batch: the window's batch
        :type focusable: bool
        :param focusable: if the gui component can be in focus
        :type visible: bool
        :param visible: if the gui component is drawn
        """
        super().__init__(parent, name, x, y, width, height, visible)
        self.focusable = focusable
        self.interfaced = interfaced
        self.is_focus = False
        self.is_hover = False

        self.labels = {}

        self._vertex_lists = {}
        self._vertexes = {}
        self._colors = {}
        for vtype in self._vertex_types:
            self._vertex_lists[vtype] = None
            self._vertexes[vtype] = []
            self._colors[vtype] = []

    def focus_on(self):
        """
        Called when the focus enters the gui component.
        """
        if self.focusable:
            self.is_focus = True
            self.render()

    def focus_off(self):
        """
        Called when the focus leaves the gui component.
        """
        self.is_focus = False
        self.render()

    def hover_on(self):
        """
        Called when the mouse hovers on the gui component.
        """
        self.is_hover = True
        self.render()

    def hover_off(self):
        """
        Called when the mouse leaves the gui component.
        """
        self.is_hover = False
        self.render()

    def is_inside(self, x, y):
        """
        Returns if the mouse is inside the gui component.

        :type x: int
        :param x: mouse x
        :type y: int
        :param y: mouse y
        :rtype: bool
        """
        return self.x <= x < self.x + self.w and self.y <= y < self.y + self.h

    def set_visible(self, visible):
        self.visible = visible
        if visible:
            self.render()
        else:
            for vtype in self._vertex_types:
                if self._vertex_lists[vtype]:
                    self._vertex_lists[vtype].delete()
                self._vertex_lists[vtype] = None
        for label in self.labels.values():
            label.set_visible(visible)

    def add_label(self, name, x, y, text='', color=(255, 255, 255), **kwargs):
        self.labels[name] = Label(self.parent, name, x, y, text, color=color, **kwargs)

    def add_quad(self, x1, y1, x2, y2, x3, y3, x4, y4, color=(0, 0, 0), uniform=True, colors=None):
        """
        Adds a quadrilateral to be drawn.
        If uniform, draws using color parameter.
        If non-uniform, draws using colors parameter.

        :param float x1: x1
        :param float y1: y1
        :param float x2: x2
        :param float y2: y2
        :param float x3: x3
        :param float y3: y3
        :param float x4: x4
        :param float y4: y4
        :param list(int * 3) color: color
        :param bool uniform: uniform coloring
        :param list(int * 12) colors: non-uniform coloring
        """
        self._vertexes['quads'].extend((x1, y1, x2, y2, x3, y3, x4, y4))
        if uniform:
            self._colors['quads'].extend(color * 4)
        else:
            self._colors['quads'].extend(colors)

    def render(self):
        pass

    def flush(self):
        for vtype in self._vertex_types:
            if self._vertex_lists[vtype]:
                self._vertex_lists[vtype].delete()
                self._vertex_lists[vtype] = None
            if not self.visible:
                continue

            if vtype == 'quads':
                vlist = self._batch.add(len(self._vertexes[vtype]) // 2, _gl.GL_QUADS, self.og0,
                                        ('v2f', self._vertexes[vtype]), ('c3B', self._colors[vtype]))
            else:
                vlist = None
            self._vertex_lists[vtype] = vlist

        self._clear()

    def _clear(self):
        for vtype in self._vertex_types:
            self._vertexes[vtype].clear()
            self._colors[vtype].clear()

    def mouse_down(self, x, y, buttons, modifiers):
        pass

    def mouse_up(self, x, y, buttons, modifiers):
        pass

    def mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        pass

    def key_down(self, symbol, modifiers):
        pass

    def text_input(self, text):
        pass


class Button(GuiComponent):
    """
    A button class.

    :ivar x: x coord
    :ivar y: y coord
    :ivar w: width
    :ivar h: height
    :ivar text: text
    :ivar action: function called when pressed
    :ivar focusable: if the component can be in focus
    :ivar is_focus: if the component is in focus
    :ivar is_hover: if the mouse is hovering over the component
    :ivar visible: if the component is drawn
    :ivar guiobjs: dictionary of gui objects
    """

    def __init__(self, parent, name, x, y, width, height, text, action=None, argsfunc=None, visible=True, interfaced=False):
        """
        Button constructor.

        :type x: int
        :param x: x coord
        :type y: int
        :param y: y coord
        :type width: int
        :param width: width
        :type height: int
        :param height: height
        :type text: str
        :param text: text
        :type batch: pyglet.graphics.Batch
        :param batch: the window's batch
        :param action: the function called when pressed
        """
        super().__init__(parent, name, x, y, width, height, True, visible, interfaced)
        self.action = action
        self.argsfunc = argsfunc
        self.text = text
        lines = text.split('\n')
        for i in range(len(lines)):
            self.add_label('label_%d' % i, x + width / 2, y + height - (i + 1) * (height / (len(lines) + 1)), lines[i],
                           anchor_x='center', anchor_y='center', width=width, visible=visible)

    def on(self):
        super().on()
        lines = self.text.split('\n')
        for i in range(len(lines)):
            self.labels['label_%d' % i].on()

    def off(self):
        super().off()
        lines = self.text.split('\n')
        for i in range(len(lines)):
            self.labels['label_%d' % i].off()

    def mouse_up(self, x, y, buttons, modifiers):
        if self.action:
            if self.argsfunc:
                self.action(*self.argsfunc())
            else:
                self.action()
    
    def set_pos(self, x, y):
        super().set_pos(x, y)
        self.labels['label'].set_pos(x, y)

    def set_text(self, text):
        """
        Sets the button's text.

        :param str text: button text
        """
        self.labels['label'].set_text(text)

    def render(self):
        if self.is_focus:
            color = (150, 150, 150)
        elif self.is_hover:
            color = (120, 120, 120)
        else:
            color = (90, 90, 90)
        self.add_quad(*rdim(self.x, self.y, self.w, self.h), color=color)
        self.flush()


class ToggleButton(Button):
    """
    A toggle button class (linked to a BoolValue).

    :ivar x: x coord
    :ivar y: y coord
    :ivar z: z level
    :ivar w: width
    :ivar h: height
    :ivar text: text
    :ivar focusable: if the component can be in focus
    :ivar is_focus: if the component is in focus
    :ivar is_hover: if the mouse is hovering over the component
    :ivar visible: if the component is drawn
    :ivar guiobjs: dictionary of gui objects
    """

    def __init__(self, parent, name, x, y, width, height, text, boolval, visible=True, interfaced=False):
        """
        Toggle button constructor.

        :type x: int
        :param x: x coord
        :type y: int
        :param y: y coord
        :type width: int
        :param width: width
        :type height: int
        :param height: height
        :type text: str
        :param text: text
        :type boolval: BoolValue
        :param boolval: the bool value linked with the button
        :type batch: pyglet.graphics.Batch
        :param batch: the window's batch
        """
        
        # has to know value before render
        # does it render on init?
        self.boolval = boolval
        super().__init__(parent, name, x, y, width, height, text, self.toggle, None, visible, interfaced)

    def toggle(self):
        """
        Toggles the BoolValue and renders the button.
        """
        self.boolval.toggle()
        self.render()

    def set_pos(self, x, y):
        super().set_pos(x, y)
        self.labels['label'].set_pos(x, y)

    def render(self):
        if self.boolval.value:
            if self.is_focus:
                color = (50, 150, 50)
            elif self.is_hover:
                color = (30, 120, 30)
            else:
                color = (10, 90, 10)
        else:
            if self.is_focus:
                color = (150, 50, 50)
            elif self.is_hover:
                color = (120, 30, 30)
            else:
                color = (90, 10, 10)
        self.add_quad(*rdim(self.x, self.y, self.w, self.h), color=color)
        self.flush()


class Field(GuiComponent):
    accepted = ()

    def __init__(self, parent, name, x, y, w, h, field_name, valobj, visible=True, interfaced=False):
        super().__init__(parent, name, x, y, w, h, True, visible, interfaced)
        self.field_name = field_name
        self.valobj = valobj
        self.input = ''
        self.input_accepted = False
        self.input_valid = False
        self.add_label('label', x, y, self.get_label_text())

    def focus_on(self):
        self.input = ''
        self.input_accepted = False
        self.input_valid = False
        super().focus_on()

    def focus_off(self):
        self.valobj.set_val(self.input)
        self.input = ''
        super().focus_off()

    def set_pos(self, x, y):
        super().set_pos(x, y)
        self.labels['label'].set_pos(x, y)

    def key_down(self, symbol, modifiers):
        if symbol == _win.key.ENTER:
            self.focus_off()
        elif symbol == _win.key.BACKSPACE:
            if len(self.input) > 0:
                self.input = self.input[:-1]
                self.update_color()
        self.update_label()

    def text_input(self, text):
        if text in self.accepted:
            self.input += text
            self.update_color()
        self.update_label()

    def get_label_text(self):
        if self.is_focus:
            return '%s: %s' % (self.field_name, self.input)
        else:
            return '%s: %s' % (self.field_name, str(self.valobj))

    def update_label(self):
        self.labels['label'].set_text(self.get_label_text())

    def update_color(self):
        self.input_accepted, self.input_valid = self.valobj.status(self.input)
        self.render()

    def render(self):
        self.update_label()
        if self.is_focus:
            if self.input_valid:
                color = (80, 150, 80)
            elif self.input_accepted:
                color = (80, 80, 150)
            else:
                color = (150, 50, 50)
        elif self.is_hover:
            color = (120, 120, 120)
        else:
            color = (90, 90, 90)
        self.add_quad(*rdim(self.x, self.y, self.w, self.h), color=color)
        self.flush()


class NumberField(Field):
    accepted = (
        '0', '1', '2', '3',
        '4', '5', '6', '7',
        '8', '9', '.', '-',
    )


class IntField(NumberField):
    accepted = (
        '0', '1', '2', '3',
        '4', '5', '6', '7',
        '8', '9', '.', '-',
        '^',
    )

    def __init__(self, parent, name, x, y, w, h, field_name, valobj, visible=True, interfaced=False):
        if type(valobj) is not IntValue:
            raise TypeError('Value object is not a IntValue!')
        super().__init__(parent, name, x, y, w, h, field_name, valobj, visible, interfaced)


class FloatField(NumberField):
    def __init__(self, parent, name, x, y, w, h, field_name, valobj, visible=True, interfaced=False):
        if type(valobj) is not FloatValue:
            raise TypeError('Value object is not a FloatValue!')
        super().__init__(parent, name, x, y, w, h, field_name, valobj, visible, interfaced)


class ComplexField(NumberField):
    accepted = (
        '0', '1', '2', '3',
        '4', '5', '6', '7',
        '8', '9', '.', '-',
        'j',
    )

    def __init__(self, parent, name, x, y, w, h, field_name, valobj, visible=True, interfaced=False):
        if type(valobj) is not ComplexValue:
            raise TypeError('Value object is not a ComplexValue!')
        super().__init__(parent, name, x, y, w, h, field_name, valobj, visible, interfaced)


class StringField(Field):
    def __init__(self, parent, name, x, y, w, h, field_name, valobj, visible=True, interfaced=False):
        if type(valobj) is not StringValue:
            raise TypeError('Value object is not a StringValue!')
        super().__init__(parent, name, x, y, w, h, field_name, valobj, visible, interfaced)

    def focus_on(self):
        self.update_color()
        self.update_label()
        if self.focusable:
            self.is_focus = True
            self.render()

    def focus_off(self):
        self.valobj.set_val(self.input)
        self.is_focus = False
        self.render()

    def text_input(self, text):
        self.input += text
        self.update_color()
        self.update_label()

    def clear(self):
        self.input = ''
        self.valobj.set_val('')
        self.update_color()
        self.update_label()


class Slider(GuiComponent):
    def __init__(self, parent, name, x, y, w, h, valobj, low=None, high=None, updatefunc=None, visible=True, interfaced=False):
        super().__init__(parent, name, x, y, w, h, True, visible, interfaced)
        self.valobj = valobj
        self.updatefunc = updatefunc
        if low is None:
            self.low = valobj.low
            self.high = valobj.high
        else:
            self.low = low
            self.high = high
        self._slider_pos = 0
        self.update_slider_pos()

    def update_slider_pos(self):
        if self.low != self.high:
            self._slider_pos = (self.valobj.value - self.low) / (self.high - self.low)
        else:
            self._slider_pos = 0

    def set_low(self, low):
        if self.low != low and low <= self.high:
            self.low = low
            self.update_slider_pos()
            new_value = (self._slider_pos * (self.high - self.low)) + self.low
            self.valobj.set_val(new_value)
            self.render()

    def set_high(self, high):
        if self.high != high and high >= self.low:
            self.high = high
            self.update_slider_pos()
            new_value = (self._slider_pos * (self.high - self.low)) + self.low
            self.valobj.set_val(new_value)
            self.render()

    def mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        raise NotImplementedError

    def render(self):
        raise NotImplementedError


class HSlider(Slider):
    def __init__(self, parent, name, x, y, w, h, field_name, valobj, low=None, high=None, updatefunc=None, visible=True, interfaced=False):
        self.field_name = field_name
        super().__init__(parent, name, x, y, w, h, valobj, low, high, updatefunc, visible, interfaced)
        self.add_label('label', x, y, self.get_label_text())

    def set_pos(self, x, y):
        super().set_pos(x, y)
        self.labels['label'].set_pos(x, y)

    def update(self):
        self.update_slider_pos()
        self.labels['label'].set_text(self.get_label_text())
        self.render()

    def get_label_text(self):
        return self.field_name + ': ' + str(self.valobj.value)

    def render(self):
        if self.is_focus:
            color = (150, 150, 150)
        elif self.is_hover:
            color = (120, 120, 120)
        else:
            color = (90, 90, 90)
        self.add_quad(*rdim(self.x, self.y, self.w, self.h), color=color)
        self.add_quad(*rdim(self.x + self._slider_pos * self.w, self.y, 2, self.h), color=(240, 0, 240))
        self.flush()

    def mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self._slider_pos = x / self.w
        if self._slider_pos < 0:
            self._slider_pos = 0
        if self._slider_pos > 1:
            self._slider_pos = 1
        new_value = (self._slider_pos * (self.high - self.low)) + self.low
        if self.valobj.set_val(new_value):
            self.updatefunc()
        self.labels['label'].set_text(self.get_label_text())
        self.render()


class IntHSlider(HSlider):
    def __init__(self, parent, name, x, y, w, h, field_name, valobj, low=None, high=None, updatefunc=None, visible=True, interfaced=False):
        if type(valobj) is not IntValue:
            raise TypeError('Value object is not IntValue!')
        super().__init__(parent, name, x, y, w, h, field_name, valobj, low, high, updatefunc, visible, interfaced)

    def mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self._slider_pos = x / self.w
        if self._slider_pos < 0:
            self._slider_pos = 0
        if self._slider_pos > 1:
            self._slider_pos = 1
        new_value = (self._slider_pos * (self.high - self.low)) + self.low
        if self.valobj.set_val(new_value + .5):
            self.updatefunc()
        self.labels['label'].set_text(self.get_label_text())
        self.render()


class FloatHSlider(HSlider):
    def __init__(self, parent, name, x, y, w, h, field_name, valobj, low=None, high=None, updatefunc=None, visible=True, interfaced=False):
        if type(valobj) is not FloatValue:
            raise TypeError('Value object is not FloatValue!')
        super().__init__(parent, name, x, y, w, h, field_name, valobj, low, high, updatefunc, visible, interfaced)


class VSlider(Slider):
    def __init__(self, parent, name, x, y, w, h, valobj, low=None, high=None, updatefunc=None, visible=True, interfaced=False):
        super().__init__(parent, name, x, y, w, h, valobj, low, high, updatefunc, visible, interfaced)

    def render(self):
        if self.is_focus:
            color = (150, 150, 150)
        elif self.is_hover:
            color = (120, 120, 120)
        else:
            color = (90, 90, 90)
        self.add_quad(*rdim(self.x, self.y, self.w, self.h), color=color)
        self.add_quad(*rdim(self.x, self.y + self.h - self._slider_pos * self.h, self.w, 2), color=(240, 0, 240))
        self.flush()

    def mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self._slider_pos = (self.h - y) / self.h
        if self._slider_pos < 0:
            self._slider_pos = 0
        if self._slider_pos > 1:
            self._slider_pos = 1
        new_value = (self._slider_pos * (self.high - self.low)) + self.low
        if self.valobj.set_val(new_value):
            self.updatefunc()
        self.render()


class IntVSlider(VSlider):
    def __init__(self, parent, name, x, y, w, h, valobj, low=None, high=None, updatefunc=None, visible=True, interfaced=False):
        if type(valobj) is not IntValue:
            raise TypeError('Value object is not IntValue!')
        super().__init__(parent, name, x, y, w, h, valobj, low, high, updatefunc, visible, interfaced)

    def mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self._slider_pos = (self.h - y) / self.h
        if self._slider_pos < 0:
            self._slider_pos = 0
        if self._slider_pos > 1:
            self._slider_pos = 1
        new_value = (self._slider_pos * (self.high - self.low)) + self.low
        if self.valobj.set_val(new_value + .5):
            self.updatefunc()
        self.render()

'''
class LabelRowSlider(IntVSlider):
    def __init__(self, parent, name, x, y, w, h, valobj, labelrow, low=None, high=None, updatefunc=None, visible=True):
        super().__init__(parent, name, x, y, w, h, valobj, low, high, visible, True)
        self.labelrow = labelrow

    def mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        super().mouse_drag(x, y, dx, dy, buttons, modifiers)
        if self.labelrow:
            self.labelrow.render()
'''


class LabelRow(GuiComponent):
    def __init__(self, parent, name, x, y, width, height, maxchars, maxrows, strfunc, visible=True, interfaced=False):
        super().__init__(parent, name, x, y, width, height, False, visible, interfaced)
        self.maxchars = maxchars
        self.maxrows = maxrows
        self.strfunc = strfunc

        parent.add_int_value(name + '__intvalue', limit='ul', low=0, high=0)
        self.valobj = parent.get_valobj(name + '__intvalue')
        # parent.sliders[name + '__intvslider'] = LabelRowSlider(parent, name, x + width - 10, y, 10, height, self.valobj, self, visible=visible)

        parent.sliders[name + '__intvslider'] = IntVSlider(parent, name, x + width - 10, y, 10, height, self.valobj,
                                                           updatefunc=lambda: self.render(), visible=visible)
        self.slider = parent.sliders[name + '__intvslider']

        for i in range(maxrows):
            self.add_label(i, x + 5, y + height - (i + 1) * (height / maxrows) + 5, '')

    def render(self):
        self.add_quad(*rdim(self.x, self.y, self.w - 10, self.h), color=(50, 50, 50))
        for i in range(self.maxrows):
            self.labels[i].set_text('')
        rows = self.strfunc()
        if len(rows) > 5:
            diff = len(rows) - 5 - self.valobj.high
            self.valobj.high = len(rows) - 5
            if diff < 0:
                self.valobj.set_val(self.valobj.value + diff)
            self.slider.set_high(len(rows) - 5)
            self.slider.update_slider_pos()
            offs = self.valobj.value
            for i in range(offs, offs + 5):
                row = rows[i]
                if len(row) > self.maxchars:
                    row = row[:self.maxchars - 3] + '...'
                self.labels[i - offs].set_text(row)
        else:
            self.slider.set_high(0)
            self.slider.update_slider_pos()
            for i, row in enumerate(rows):
                if len(row) > self.maxchars:
                    row = row[:self.maxchars - 3] + '...'
                self.labels[i].set_text(row)
        self.flush()
        self.slider.render()


class Box(GuiComponent):
    def __init__(self, parent, name, x, y, width, height, visible=True, interfaced=False):
        super().__init__(parent, name, x, y, width, height, False, visible, interfaced)
        self.name = name
