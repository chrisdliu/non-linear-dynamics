import pyglet.gl as _gl
import pyglet.graphics as _graphics
import pyglet.text as _text
import pyglet.window as _win

from pyg.valset import *


class GuiObj:
    """
    Superclass for all gui objects
    """

    # box group
    _group_1 = _graphics.OrderedGroup(1)
    # label group
    _group_2 = _graphics.OrderedGroup(2)

    def __init__(self, x, y, w, h, batch, focusable=False, visible=True):
        """
        GuiObj initializer
        :type x: int
        :param x: x coord
        :type y: int
        :param y: y coord
        :type w: int
        :param w: width
        :type h: int
        :param h: height
        :type batch: pyglet.graphics.Batch
        :param batch: the batch to add its vertex lists to
        :type focusable: bool
        :param focusable:
        :type visible: bool
        :param visible: if the object is visible (is drawn)
        """
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self._batch = batch
        self.focusable = focusable
        self.visible = visible
        self.is_focus = False
        self.is_hover = False
        self._vertex_lists = []

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

    def enter(self):
        """
        Called when the guiobj is in focus
        """
        if self.focusable:
            self.is_focus = True
            self.render()

    def exit(self):
        """
        Called when the guiobj focus leaves
        :return:
        """
        self.is_focus = False
        self.render()

    def hover_on(self):
        """
        Called when the mouse hovers on the guiobj
        """
        self.is_hover = True
        self.render()

    def hover_off(self):
        """
        Called when the mouse leaves the guiobj
        :return:
        """
        self.is_hover = False
        self.render()

    def set_pos(self, x, y):
        """
        Sets the position of the guiobj
        :type x: int
        :param x: x coord
        :type x: int
        :param y: y coord
        """
        self.x = x
        self.y = y

    def set_size(self, w, h):
        """
        Sets the size of the guiobj
        :type w: int
        :param w: width
        :type h: int
        :param h: height
        """
        self.w = w
        self.h = h

    def set_visible(self, visible):
        """
        Sets the guiobj's visible field
        If visible is True, it is rendered
        If visible is False, it is unrendered
        :type visible: bool
        :param visible: visible
        """
        if visible:
            self.render()
        else:
            self._clear()
        self.visible = visible

    def is_inside(self, x, y):
        """
        Returns if the mouse is inside the guiobj
        :type x: int
        :param x: mouse x
        :type y: int
        :param y: mouse y
        :rtype: bool
        """
        return self.x <= x < self.x + self.w and self.y <= y < self.y + self.h

    def _add_vlist(self, vlist):
        """
        Adds a vertex list
        :param vlist: a vertex list
        """
        self._vertex_lists.append(vlist)

    def _clear(self):
        """
        Deletes all vertex lists and removes them
        """
        for vlist in self._vertex_lists:
            vlist.delete()
        self._vertex_lists.clear()

    def render(self):
        """
        Renders the guiobj
        Should be overridden
        """
        pass

    def key_down(self, symbol, modifiers):
        pass

    def text_input(self, text):
        pass

    def mouse_down(self, x, y, buttons, modifiers):
        pass

    def mouse_up(self, x, y, buttons, modifiers):
        pass

    def mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        pass


class Label(GuiObj):
    def __init__(self, x, y, text, batch, color=(255, 255, 255)):
        super().__init__(x, y, 0, 0, batch)
        self._pyglet_label = _text.Label(text, font_name='Menlo', font_size=8, x=x, y=y, batch=batch,
                                               group=self._group_2, color=(*color, 255))

    def set_text(self, text):
        self._pyglet_label.text = text

    def set_pos(self, x, y):
        super().set_pos(x, y)
        self._pyglet_label.x = x
        self._pyglet_label.y = y


class Box(GuiObj):
    def __init__(self, x, y, w, h, batch, color=(255, 255, 255)):
        super().__init__(x, y, w, h, batch)
        self.color = color

    def set_color(self, r, g, b):
        self.color = (r, g, b)
        self.render()

    def render(self):
        self._clear()
        self._add_vlist(self._batch.add(4, _gl.GL_QUADS, self._group_1,
                                        ('v2f', (self.x, self.y, self.x + self.w, self.y,
                                                self.x + self.w, self.y + self.h, self.x, self.y + self.h)),
                                        ('c3B', self.color * 4)))


class Field(GuiObj):
    accepted = ()

    def __init__(self, x, y, w, h, name, valobj, batch):
        super().__init__(x, y, w, h, batch, True)
        self.name = name
        self.valobj = valobj
        self.input = ''
        self.input_accepted = False
        self.input_valid = False
        self._label = Label(x, y, self.get_label_text(), batch)
        self._box = Box(x, y, w, h, batch, color=(90, 90, 90))

    def enter(self):
        self.input = ''
        self.input_accepted = False
        self.input_valid = False
        super().enter()

    def exit(self):
        self.valobj.set_val_cast(self.input)
        self.input = ''
        super().exit()

    def set_pos(self, x, y):
        super().set_pos(x, y)
        self._label.set_pos(x, y)

    def key_down(self, symbol, modifiers):
        if symbol == _win.key.ENTER:
            self.exit()
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
            return '%s: %s' % (self.name, self.input)
        else:
            return '%s: %s' % (self.name, str(self.valobj))

    def update_label(self):
        self._label.set_text(self.get_label_text())

    def update_color(self):
        parsed = self.valobj.parse(self.input)
        if parsed is not None:
            self.input_accepted = True
            if self.valobj.is_valid(parsed):
                self.input_valid = True
            else:
                self.input_valid = False
        else:
            self.input_accepted = False
            self.input_valid = False
        self.render()

    def render(self):
        self._clear()
        self.update_label()
        if self.is_focus:
            if self.input_valid:
                self._box.set_color(80, 150, 80)
            elif self.input_accepted:
                self._box.set_color(80, 80, 150)
            else:
                self._box.set_color(150, 50, 50)
        elif self.is_hover:
            self._box.set_color(120, 120, 120)
        else:
            self._box.set_color(90, 90, 90)
        self._box.render()


class NumberField(Field):
    accepted = (
        '0', '1', '2', '3',
        '4', '5', '6', '7',
        '8', '9', '.', '-',
    )


class FloatField(NumberField):
    def __init__(self, x, y, w, h, name, valobj, batch):
        if type(valobj) is not FloatValue:
            raise TypeError('Value object is not a FloatValue!')
        super().__init__(x, y, w, h, name, valobj, batch)


class IntField(NumberField):
    def __init__(self, x, y, w, h, name, valobj, batch):
        if type(valobj) is not IntValue:
            raise TypeError('Value object is not a IntValue!')
        super().__init__(x, y, w, h, name, valobj, batch)


class ComplexField(NumberField):
    accepted = (
        '0', '1', '2', '3',
        '4', '5', '6', '7',
        '8', '9', '.', '-',
        'j',
    )

    def __init__(self, x, y, w, h, name, valobj, batch):
        if type(valobj) is not ComplexValue:
            raise TypeError('Value object is not a ComplexValue!')
        super().__init__(x, y, w, h, name, valobj, batch)


class Button(GuiObj):
    def __init__(self, x, y, w, h, text, batch, action=None):
        super().__init__(x, y, w, h, batch, True)
        self.action = action
        self._text = text
        self._label = Label(x, y, text, batch)
        self._box = Box(x, y, w, h, batch, color=(90, 90, 90))

    def set_pos(self, x, y):
        super().set_pos(x, y)
        self._label.set_pos(x, y)

    def set_visible(self, visible):
        super().set_visible(visible)
        if visible:
            self.set_text(self._text)
        else:
            self.set_text('')

    def mouse_up(self, *args, **kwargs):
        if self.action:
            self.action(*args, **kwargs)

    def set_text(self, text):
        self._label.set_text(text)

    def render(self):
        self._clear()
        if self.is_focus:
            self._box.set_color(150, 150, 150)
        elif self.is_hover:
            self._box.set_color(120, 120, 120)
        else:
            self._box.set_color(90, 90, 90)
        self._box.render()


class ToggleButton(Button):
    def __init__(self, x, y, w, h, text, boolval, batch):
        self.boolval = boolval
        super().__init__(x, y, w, h, text, batch, action=self.toggle)

    def toggle(self):
        self.boolval.toggle()
        self.render()

    def set_pos(self, x, y):
        super().set_pos(x, y)
        self._label.set_pos(x, y)

    def render(self):
        self._clear()
        if self.boolval.value:
            if self.is_focus:
                self._box.set_color(50, 150, 50)
            elif self.is_hover:
                self._box.set_color(30, 120, 30)
            else:
                self._box.set_color(10, 90, 10)
        else:
            if self.is_focus:
                self._box.set_color(150, 50, 50)
            elif self.is_hover:
                self._box.set_color(120, 30, 30)
            else:
                self._box.set_color(90, 10, 10)
        self._box.render()


class Slider(GuiObj):
    def __init__(self, x, y, w, h, offs, field_name, valobj, low, high, batch):
        super().__init__(x, y, w, h, batch, True)
        self.offs = offs
        self.field_name = field_name
        self.valobj = valobj
        self.low = low
        self.high = high
        self._slider_pos = (valobj.value - low) / (high - low)
        self._label = Label(x, y, self.get_label_text(), batch)
        self._box = Box(x, y, w, h, batch, color=(90, 90, 90))
        self._bar = Box(x + self._slider_pos * w + offs, y, 2, h, batch, color=(240, 0, 240))

    def update_pos(self):
        self._slider_pos = (self.valobj.value - self.low) / (self.high - self.low)
        self._label.set_text(self.get_label_text())
        self.render()

    def get_label_text(self):
        return self.field_name + ': ' + str(self.valobj.value)

    def is_inside(self, x, y):
        return self.x <= x < self.x + self.w + self.offs and self.y <= y < self.y + self.h

    def render(self):
        self._clear()
        if self.is_focus:
            self._box.set_color(150, 150, 150)
        elif self.is_hover:
            self._box.set_color(120, 120, 120)
        else:
            self._box.set_color(90, 90, 90)
        self._box.render()
        self._bar.set_pos(self.x + self._slider_pos * self.w + self.offs, self.y)
        self._bar.render()

    def mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self._slider_pos = (x - self.offs) / self.w
        if self._slider_pos < 0:
            self._slider_pos = 0
        if self._slider_pos > 1:
            self._slider_pos = 1
        new_value = (self._slider_pos * (self.high - self.low)) + self.low
        self.valobj.set_val_cast(new_value)
        self._label.set_text(self.get_label_text())
        self.render()


class IntSlider(Slider):
    def __init__(self, x, y, w, h, offs, field_name, valobj, low, high, batch):
        if type(valobj) is not IntValue:
            raise TypeError('Value object is not IntValue!')
        super().__init__(x, y, w, h, offs, field_name, valobj, low, high, batch)


class FloatSlider(Slider):
    def __init__(self, x, y, w, h, offs, field_name, valobj, low, high, batch):
        if type(valobj) is not FloatValue:
            raise TypeError('Value object is not FloatValue!')
        super().__init__(x, y, w, h, offs, field_name, valobj, low, high, batch)


__imports__ = (GuiObj, Label, Box,)
