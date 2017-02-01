import pyglet.gl as _gl
import pyglet.graphics as _graphics
import pyglet.text as _text
import pyglet.window as _win

from pyg.valset import *


class GuiObj:
    """
    Basic gui object class (boxes, labels).

    :var x: x coord
    :var y: y coord
    :var z: z level
    :var w: width
    :var h: height
    :var w: width
    :var h: height
    :var visible: if the gui object is drawn
    """

    #: label group (z level 6)
    label_group = _graphics.OrderedGroup(6)

    def __init__(self, x, y, w, h, batch, z=0, visible=True):
        """
        Gui object constructor.

        :type x: float
        :param x: x coord
        :type y: float
        :param y: y coord
        :type w: float
        :param w: width
        :type h: float
        :param h: height
        :type batch: pyglet.graphics.Batch
        :param batch: the window's batch
        :type z: int
        :param z: z level
        :type visible: bool
        :param visible: if the gui object is drawn
        """
        self.x = x
        self.y = y
        self.z = z
        self.w = w
        self.h = h
        self._batch = batch
        self._vertex_lists = []
        self.group = _graphics.OrderedGroup(z)
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

    def set_size(self, w, h):
        """
        Sets the gui object's dimensions

        :type w: int
        :param w: width
        :type h: int
        :param h: height
        :return:
        """
        self.w = w
        self.h = h

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
        else:
            self._clear()

    def _add_vlist(self, vlist):
        self._vertex_lists.append(vlist)

    def render(self):
        """
        Renders the gui object.
        Should clear and re-add its vertex lists.
        Should be overridden.
        """
        pass

    def _clear(self):
        for vlist in self._vertex_lists:
            vlist.delete()
        self._vertex_lists.clear()


class Label(GuiObj):
    """
    A label class (text).

    :var x: x coord
    :var y: y coord
    :var z: z level
    :var w: width
    :var h: height
    :var text: text
    :var color: color
    :var visible: if the gui object is drawn
    """

    def __init__(self, x, y, text, batch, color=(255, 255, 255)):
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
        super().__init__(x, y, 0, 0, batch)
        self.text = text
        self._pyglet_label = _text.Label(text, font_name='Menlo', font_size=8, x=x, y=y, batch=batch,
                                         group=self.label_group, color=(*color, 255))

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
        self._pyglet_label.text = text

    def set_pos(self, x, y):
        super().set_pos(x, y)
        self._pyglet_label.x = x
        self._pyglet_label.y = y


class Box(GuiObj):
    """
    A box class.

    :var x: x coord
    :var y: y coord
    :var z: z level
    :var w: width
    :var h: height
    :var color: color
    :var visible: if the box is drawn
    """

    def __init__(self, x, y, w, h, batch, z=0, color=(255, 255, 255)):
        """
        Box constructor.

        :type x: int
        :param x: x coord
        :type y: int
        :param y: y coord
        :type w: int
        :param w: width
        :type h: int
        :param h: height
        :type batch: pyglet.graphics.Batch
        :param batch: the window's batch
        :type z: int
        :param z: z level
        :type color: list(int * 3)
        :param color: color
        """
        super().__init__(x, y, w, h, batch, z=z)
        self.color = color

    def set_color(self, r, g, b):
        """
        Sets the color of the box.

        :type r: int
        :param r: red
        :type g: int
        :param g: green
        :type b: int
        :param b: blue
        """
        self.color = (r, g, b)

    def render(self):
        self._clear()
        self._add_vlist(self._batch.add(4, _gl.GL_QUADS, self.group,
                                        ('v3f', (self.x, self.y, self.z, self.x + self.w, self.y, self.z,
                                                 self.x + self.w, self.y + self.h, self.z, self.x, self.y + self.h, self.z)),
                                        ('c3B', self.color * 4)))


class GuiComp:
    """
    Base gui component (buttons, fields, sliders) class.

    :var x: x coord
    :var y: y coord
    :var z: z level
    :var w: width
    :var h: height
    :var w: width
    :var h: height
    :var focusable: if the component can be in focus
    :var visible: if the component is drawn
    """

    def __init__(self, x, y, w, h, batch, focusable=False, visible=True):
        """
        Gui component constructor.

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
        :param focusable: if the gui component can be in focus
        :type visible: bool
        :param visible: if the gui component is drawn
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
        self.guiobjs = {}

    def set_pos(self, x, y):
        """
        Sets the position of the gui component.

        :type x: int
        :param x: x coord
        :type x: int
        :param y: y coord
        """
        self.x = x
        self.y = y

    def set_size(self, w, h):
        """
        Sets the size of the gui component.

        :type w: int
        :param w: width
        :type h: int
        :param h: height
        """
        self.w = w
        self.h = h

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

    def set_visible(self, visible):
        """
        Sets the guiobj's visible field.
        If visible is True, it is rendered.
        If visible is False, it is unrendered.

        :type visible: bool
        :param visible: visible
        """
        self.visible = visible
        for guiobj in self.guiobjs.values():
            guiobj.set_visible(visible)
        if visible:
            self.render()

    def focus_on(self):
        """
        Called when the focus is the gui component.
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

    def add_label(self, name, x, y, text, color=(255, 255, 255)):
        """
        Adds a label to the gui object dictionary.

        :type name: str
        :param name: the label's name
        :type x: float
        :param x: x coord
        :type y: float
        :param y: y coord
        :type text: str
        :param text: text
        :type color: list(int * 3)
        :param color: color
        """
        self.guiobjs[name] = Label(x, y, text, self._batch, color)

    def add_box(self, name, x, y, w, h, z=0, color=(255, 255, 255)):
        """
        Adds a box to the gui object dictionary.

        :type name: str
        :param name: the box's name
        :type x: float
        :param x: x coord
        :type y: float
        :param y: y coord
        :type w: float
        :param w: widht
        :type h: float
        :param h: height
        :type z: int
        :param z: z level
        :type text: str
        :param text: text
        :type color: list(int * 3)
        :param color: color
        """
        self.guiobjs[name] = Box(x, y, w, h, self._batch, z, color)

    def render(self):
        """
        Sets parameters for the gui objects.
        Should be overridden.
        """
        pass

    def flush(self):
        """
        Renders all the gui objects
        """
        for guiobj in self.guiobjs.values():
            guiobj.render()

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


class Button(GuiComp):
    """
    A button class.

    :var x: x coord
    :var y: y coord
    :var z: z level
    :var w: width
    :var h: height
    :var text: text
    :var action: function called when pressed
    :var focusable: if the component can be in focus
    :var visible: if the component is drawn
    """

    def __init__(self, x, y, w, h, text, batch, action=None):
        """
        Button constructor.

        :type x: int
        :param x: x coord
        :type y: int
        :param y: y coord
        :type w: int
        :param w: width
        :type h: int
        :param h: height
        :type text: str
        :param text: text
        :type batch: pyglet.graphics.Batch
        :param batch: the batch to add its vertex lists to
        :type action: function
        :param action: the function called when pressed
        """
        super().__init__(x, y, w, h, batch, True)
        self.action = action
        self.add_label('label', x, y, text)
        self.add_box('box', x, y, w, h, color=(90, 90, 90))

    def set_pos(self, x, y):
        super().set_pos(x, y)
        self.guiobjs['label'].set_pos(x, y)
        self.guiobjs['box'].set_pos(x, y)

    def mouse_up(self, *args, **kwargs):
        if self.action:
            self.action(*args, **kwargs)

    def set_text(self, text):
        """
        Sets the button's text.

        :type text: str
        :param text: text
        """
        self.guiobjs['label'].set_text(text)

    def render(self):
        if self.is_focus:
            self.guiobjs['box'].set_color(150, 150, 150)
        elif self.is_hover:
            self.guiobjs['box'].set_color(120, 120, 120)
        else:
            self.guiobjs['box'].set_color(90, 90, 90)
        self.flush()


class ToggleButton(Button):
    """
    A toggle button class (linked to a BoolValue).

    :var x: x coord
    :var y: y coord
    :var z: z level
    :var w: width
    :var h: height
    :var text: text
    :var action: function called when pressed
    :var focusable: if the component can be in focus
    :var visible: if the component is drawn
    """

    def __init__(self, x, y, w, h, text, boolval, batch):
        """
        Toggle button constructor.

        :type x: int
        :param x: x coord
        :type y: int
        :param y: y coord
        :type w: int
        :param w: width
        :type h: int
        :param h: height
        :type text: str
        :param text: text
        :type boolval: BoolValue
        :param boolval: the bool value linked with the button
        :type batch: pyglet.graphics.Batch
        :param batch: the batch to add its vertex lists to
        """
        self.boolval = boolval
        super().__init__(x, y, w, h, text, batch, action=self.toggle)

    def toggle(self):
        """
        Toggles the BoolValue and renders the button.
        """
        self.boolval.toggle()
        self.render()

    def set_pos(self, x, y):
        super().set_pos(x, y)
        self.guiobjs['label'].set_pos(x, y)
        self.guiobjs['box'].set_pos(x, y)

    def render(self):
        if self.boolval.value:
            if self.is_focus:
                self.guiobjs['box'].set_color(50, 150, 50)
            elif self.is_hover:
                self.guiobjs['box'].set_color(30, 120, 30)
            else:
                self.guiobjs['box'].set_color(10, 90, 10)
        else:
            if self.is_focus:
                self.guiobjs['box'].set_color(150, 50, 50)
            elif self.is_hover:
                self.guiobjs['box'].set_color(120, 30, 30)
            else:
                self.guiobjs['box'].set_color(90, 10, 10)
        self.flush()


class Field(GuiComp):
    accepted = ()

    def __init__(self, x, y, w, h, name, valobj, batch):
        super().__init__(x, y, w, h, batch, True)
        self.name = name
        self.valobj = valobj
        self.input = ''
        self.input_accepted = False
        self.input_valid = False
        self.add_label('label', x, y, self.get_label_text())
        self.add_box('box', x, y, w, h, color=(90, 90, 90))

    def focus_on(self):
        self.input = ''
        self.input_accepted = False
        self.input_valid = False
        super().focus_on()

    def focus_off(self):
        self.valobj.set_val_cast(self.input)
        self.input = ''
        super().focus_off()

    def set_pos(self, x, y):
        super().set_pos(x, y)
        self.guiobjs['label'].set_pos(x, y)
        self.guiobjs['box'].set_pos(x, y)

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
            return '%s: %s' % (self.name, self.input)
        else:
            return '%s: %s' % (self.name, str(self.valobj))

    def update_label(self):
        self.guiobjs['label'].set_text(self.get_label_text())

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
        self.update_label()
        if self.is_focus:
            if self.input_valid:
                self.guiobjs['box'].set_color(80, 150, 80)
            elif self.input_accepted:
                self.guiobjs['box'].set_color(80, 80, 150)
            else:
                self.guiobjs['box'].set_color(150, 50, 50)
        elif self.is_hover:
            self.guiobjs['box'].set_color(120, 120, 120)
        else:
            self.guiobjs['box'].set_color(90, 90, 90)
        self.flush()


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


class Slider(GuiComp):
    def __init__(self, x, y, w, h, offs, field_name, valobj, low, high, batch):
        super().__init__(x, y, w, h, batch, True)
        self.offs = offs
        self.field_name = field_name
        self.valobj = valobj
        self.low = low
        self.high = high
        self._slider_pos = (valobj.value - low) / (high - low)
        self.add_label('label', x, y, self.get_label_text())
        self.add_box('box', x, y, w, h, color=(90, 90, 90))
        self.add_box('bar', x + self._slider_pos * w + offs, y, 2, h, z=1, color=(240, 0, 240))

    def update_pos(self):
        self._slider_pos = (self.valobj.value - self.low) / (self.high - self.low)
        self.guiobjs['label'].set_text(self.get_label_text())
        self.render()

    def get_label_text(self):
        return self.field_name + ': ' + str(self.valobj.value)

    def is_inside(self, x, y):
        return self.x <= x < self.x + self.w + self.offs and self.y <= y < self.y + self.h

    def render(self):
        if self.is_focus:
            self.guiobjs['box'].set_color(150, 150, 150)
        elif self.is_hover:
            self.guiobjs['box'].set_color(120, 120, 120)
        else:
            self.guiobjs['box'].set_color(90, 90, 90)
        self.guiobjs['bar'].set_pos(self.x + self._slider_pos * self.w + self.offs, self.y)
        self.flush()

    def mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self._slider_pos = (x - self.offs) / self.w
        if self._slider_pos < 0:
            self._slider_pos = 0
        if self._slider_pos > 1:
            self._slider_pos = 1
        new_value = (self._slider_pos * (self.high - self.low)) + self.low
        self.valobj.set_val_cast(new_value)
        self.guiobjs['label'].set_text(self.get_label_text())
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
