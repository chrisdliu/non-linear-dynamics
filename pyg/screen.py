import pyglet.graphics as _graphics
import pyglet.window as _win

from pyglet.gl import *


class Screen:
    """
    A base screen class
    """

    _vertex_types = ('points', 'lines', 'line_strip', 'triangles', 'quads')

    def __init__(self, x, y, width, height, valset, bg=(255, 255, 255), visible=True, active=True):
        """
        Screen initializer
        :type x: int
        :param x: x coord
        :type y: int
        :param y: y coord
        :type width: int
        :param width: width
        :type height: int
        :param height: height
        :type valset: pyg.valset.Valset
        :param valset: the window's value set
        :type bg: tuple (rgb, length 3)
        :param bg:
        :param visible:
        :param active:
        """
        self.x = x
        self.y = y
        self.w = width
        self.h = height
        # window width and height for glOrtho
        self._ww = 0
        self._wh = 0
        self.visible = visible
        self.active = active

        self._batch = _graphics.Batch()
        self._vertex_lists = {}
        self._vertexes = {}
        self._colors = {}
        self._vertex_lists['bg'] = None
        for vtype in self._vertex_types:
            self._vertex_lists[vtype] = None
            self._vertexes[vtype] = []
            self._colors[vtype] = []

        self.bg = bg
        self.set_bg(bg)

        self.valset = valset

    # region visible and active set functions
    def set_visible(self, visible):
        """
        Sets screen.visible
        if True, renders the screen
        if False, deletes the screen's vertex lists
        :param visible: bool
        """
        self.visible = visible
        if visible:
            self.render()
        else:
            for vtype in self._vertex_lists.keys():
                if self._vertex_lists[vtype]:
                    self._vertex_lists[vtype].delete()
                self._vertex_lists[vtype] = None

    def set_active(self, active):
        """
        Sets screen.active
        Window will call screen.tick if the screen is active
        :param active: bool
        """
        self.active = active

    def on(self):
        """
        Calls set_visible and set_active with True
        """
        self.set_active(True)
        self.set_visible(True)

    def off(self):
        """
        Calls set_visible and set_active with False
        """
        self.set_active(False)
        self.set_visible(False)
    # endregion

    # region valset functions
    def get_val(self, name):
        """
        Returns a value from the valset
        :param name: value's name
        :return: value
        """
        return self.valset.get_val(name)

    def set_val(self, name, new_value):
        """
        Sets a value to a new value
        :param name: value's name
        :param new_value: new value
        """
        self.valset.set_val(name, new_value)

    def get_obj(self, name):
        """
        Returns a valobj from the valset
        :param name: valobj's name
        :return: valobj
        """
        return self.valset.get_obj(name)
    # endregion

    # region vertex set functions
    def set_points(self, vertexes, colors):
        self._vertexes['points'] = vertexes
        self._colors['points'] = colors

    def set_lines(self, vertexes, colors):
        self._vertexes['lines'] = vertexes
        self._colors['lines'] = colors

    def set_line_strip(self, vertexes, colors):
        self._vertexes['line_strip'] = vertexes
        self._colors['line_strip'] = colors

    def set_triangles(self, vertexes, colors):
        self._vertexes['triangles'] = vertexes
        self._colors['triangles'] = colors

    def set_quads(self, vertexes, colors):
        self._vertexes['quads'] = vertexes
        self._colors['quads'] = colors
    # endregion

    # region to be implemented functions
    def set_bg(self, color):
        raise NotImplementedError

    def add_point(self, *args, **kwargs):
        raise NotImplementedError

    def add_points(self, *args, **kwargs):
        raise NotImplementedError

    def add_line(self, *args, **kwargs):
        raise NotImplementedError

    def add_triangle(self, *args, **kwargs):
        raise NotImplementedError

    def add_quad(self, *args, **kwargs):
        raise NotImplementedError
    # endregion

    def flush(self):
        """
        Deletes the current vertex lists
        If the screen is visible, adds the vertexes in the buffer to the batch
        Clears the buffer
        """
        for vtype in self._vertex_types:
            if self._vertex_lists[vtype]:
                self._vertex_lists[vtype].delete()
                self._vertex_lists[vtype] = None
            if not self.visible:
                continue

            if vtype == 'points':
                vlist = self._batch.add(len(self._vertexes[vtype]) // 3, GL_POINTS, None,
                                        ('v3f', self._vertexes[vtype]), ('c3B', self._colors[vtype]))
            elif vtype == 'lines':
                vlist = self._batch.add(len(self._vertexes[vtype]) // 3, GL_LINES, None,
                                        ('v3f', self._vertexes[vtype]), ('c3B', self._colors[vtype]))
            elif vtype == 'line_strip':
                vlist = self._batch.add(len(self._vertexes[vtype]) // 3, GL_LINE_STRIP, None,
                                        ('v3f', self._vertexes[vtype]), ('c3B', self._colors[vtype]))
            elif vtype == 'triangles':
                vlist = self._batch.add(len(self._vertexes[vtype]) // 3, GL_TRIANGLES, None,
                                        ('v3f', self._vertexes[vtype]), ('c3B', self._colors[vtype]))
            elif vtype == 'quads':
                vlist = self._batch.add(len(self._vertexes[vtype]) // 3, GL_QUADS, None,
                                        ('v3f', self._vertexes[vtype]), ('c3B', self._colors[vtype]))
            else:
                vlist = None
            self._vertex_lists[vtype] = vlist

        self._clear()

    def _clear(self):
        """
        Clears the buffer arrays
        """
        for vtype in self._vertex_types:
            self._vertexes[vtype] = []
            self._colors[vtype] = []

    def draw(self):
        """
        Draws its batch
        """
        self._batch.draw()

    # region to be overridden functions
    def render(self):
        pass

    def mouse_move(self, x, y, dx, dy):
        pass

    def mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        pass

    def mouse_down(self, x, y, button, modifier):
        pass

    def mouse_up(self, x, y, button, modifiers):
        pass

    def key_down(self, symbol, modifiers):
        pass

    def key_up(self, symbol, modifiers):
        pass

    def tick(self):
        pass

    def resize(self, width, height):
        pass
    # endregion

    def is_inside(self, x, y):
        """
        Returns if (x, y) is inside the screen
        :param x: x
        :param y: y
        :return: if the point is inside the screen
        """
        return 0 <= x - self.x < self.w and 0 <= y - self.y < self.h

    def on_resize(self, width, height):
        self._ww = width
        self._wh = height
        self.resize(width, height)
        self.set_bg(self.bg)

    def set_pos(self, x, y):
        """
        Sets the screen's position
        :param x: x
        :param y: y
        """
        self.x = x
        self.y = y


class Screen2D(Screen):
    def draw(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self._ww, 0, self._wh, -1001, 1001)
        glMatrixMode(GL_MODELVIEW)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_SCISSOR_TEST)
        glScissor(self.x, self.y, self.w, self.h)

        glPushMatrix()
        glTranslatef(self.x + .1, self.y + .1, 0)

        self._batch.draw()

        glPopMatrix()

        glDisable(GL_SCISSOR_TEST)
        glDisable(GL_DEPTH_TEST)

    def set_bg(self, color):
        if self._vertex_lists['bg']:
            self._vertex_lists['bg'].delete()
        vlist = self._batch.add(4, GL_QUADS, None,
                                ('v3f', (0, 0, -1000, self.w, 0, -1000,
                                         self.w, self.h, -1000, 0, self.h, -1000)),
                                ('c3B', color * 4))
        self._vertex_lists['bg'] = vlist

    def add_point(self, x, y, z=0, color=(0, 0, 0)):
        self._vertexes['points'].extend((x, y, z))
        self._colors['points'].extend(color)

    def add_points(self, points, colors):
        self._vertexes['points'].extend(points)
        self._colors['points'].extend(colors)

    def add_line(self, x1, y1, x2, y2, z=0, color=(0, 0, 0)):
        self._vertexes['lines'].extend((x1, y1, z, x2, y2, z))
        self._colors['lines'].extend(color * 2)

    def add_triangle(self, x1, y1, x2, y2, x3, y3, z=0, color=(0, 0, 0), uniform=True, colors=([0] * 9)):
        self._vertexes['triangles'].extend((x1, y1, z, x2, y2, z, x3, y3, z))
        if uniform:
            self._colors['triangles'].extend(color * 3)
        else:
            self._colors['triangles'].extend(colors)

    def add_quad(self, x1, y1, x2, y2, x3, y3, x4, y4, z=0, color=(0, 0, 0), uniform=True, colors=([0] * 12)):
        self._vertexes['quads'].extend((x1, y1, z, x2, y2, z, x3, y3, z, x4, y4, z))
        if uniform:
            self._colors['quads'].extend(color * 4)
        else:
            self._colors['quads'].extend(colors)


class GraphScreen(Screen2D):
    def __init__(self, x, y, width, height, gx, gy, gw, gh, valset, zoom_valobj, bg=(255, 255, 255), visible=True, active=True):
        super().__init__(x, y, width, height, valset, bg, visible, active)
        # original width / height
        self._ow = width
        self._oh = height
        self.set_graph_coords(gx, gy, gw, gh)
        self.set_graph_minmax()
        self.reset_to(gx, gy, gw, gh)

        self.zoom_valobj = zoom_valobj
        self.total_zoom = 1
        self.drag = False
        # offset for drag
        self.offsx = 0
        self.offsy = 0

    def set_graph_minmax(self):
        """
        Sets the min/max x and y coordinates on the graph
        """
        self.min_gx = self.gx - self.gw / 2
        self.max_gx = self.gx + self.gw / 2
        self.min_gy = self.gy - self.gh / 2
        self.max_gy = self.gy + self.gh / 2

    def reset_screen(self):
        """
        Resets the graph and renders the screen
        """
        self.reset_graph()
        self.total_zoom = 1
        self.render()

    def reset_graph(self):
        """
        Resets the graph to its original coordinates
        """
        self.gx = self._ogx
        self.gy = self._ogy
        self.gw = self._ogw * (self.w / self._ow)
        self.gh = self._ogh * (self.h / self._oh)
        self.set_graph_minmax()

    def reset_to(self, gx, gy, gw, gh):
        """
        Changes the coordinates the graph resets to
        :param gx: reset graph x
        :param gy: reset graph y
        :param gw: reset graph width
        :param gh: reset graph height
        """
        self._ogx = gx
        self._ogy = gy
        self._ogw = gw
        self._ogh = gh

    def set_graph_coords(self, gx, gy, gw, gh):
        self.gx = gx
        self.gy = gy
        self.gw = gw
        self.gh = gh

    def set_graph_view(self, gx, gy, zoom):
        self.gx = gx
        self.gy = gy
        self.total_zoom = zoom
        sqrt_z = zoom ** .5
        self.gw = self._ogw / sqrt_z
        self.gh = self.gw * self.h / self.w

    def resize(self, width, height):
        """
        Resizes the screen based on the window's new width and height
        Should be overridden if screen does not take up entire window
        :param width: new window width
        :param height: new window height
        """
        self.refit(width, width)

    def refit(self, width, height):
        """
        Sets the screen's width and height and changes the graph's width and height accordingly
        :param width: new screen width
        :param height: new screen height
        """
        old_gw = self.gw
        old_gh = self.gh
        self.gw *= width / self.w
        self.gh *= height / self.h
        self.set_graph_minmax()
        self.total_zoom *= (old_gw * old_gh) / (self.gw * self.gh)
        self.w = width
        self.h = height

    # region graph move functions
    def up(self):
        """
        Moves the graph center up
        """
        self.gy += self.gh / 5
        self.set_graph_minmax()
        self.render()

    def down(self):
        """
        Moves the graph center down
        """
        self.gy -= self.gh / 5
        self.set_graph_minmax()
        self.render()

    def left(self):
        """
        Moves the graph center left
        """
        self.gx -= self.gw / 5
        self.set_graph_minmax()
        self.render()

    def right(self):
        """
        Moves the graph center right
        """
        self.gx += self.gw / 5
        self.set_graph_minmax()
        self.render()
    # endregion

    def on_screen(self, x, y):
        """
        Transforms a point on the graph to the corresponding point on the screen
        :param x: graph x
        :param y: graph y
        :return: screen x, screen y
        """
        return (x - self.gx + self.gw / 2) * self.w / self.gw, (y - self.gy + self.gh / 2) * self.h / self.gh

    def on_plot(self, x, y):
        """
        Transforms a point on the screen to the corresponding point on the graph
        :param x: screen x
        :param y: screen y
        :return: graph x, graph y
        """
        return x * self.gw / self.w + self.gx - self.gw / 2, y * self.gh / self.h + self.gy - self.gh / 2

    def mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.drag:
            self.offsx = x - self.mdownx
            self.offsy = y - self.mdowny
            #self._bg_group.offsx = -self.offsx
            #self._bg_group.offsy = -self.offsy

    def mouse_down(self, x, y, button, modifier):
        if button == _win.mouse.MIDDLE:
            self.drag = True
            self.mdownx = x
            self.mdowny = y

    def mouse_up(self, x, y, button, modifiers):
        if button == _win.mouse.LEFT:
            self.gx = self.gx - self.gw / 2 + x * self.gw / self.w
            self.gy = self.gy - self.gh / 2 + y * self.gh / self.h
            self.gw *= self.zoom_valobj.value
            self.gh *= self.zoom_valobj.value
            self.set_graph_minmax()
            self.total_zoom *= (1 / self.zoom_valobj.value) ** 2
            #print('zoomed to %.5f,%.5f with size %.9f,%.9f' % (self.gx, self.gy, self.gw, self.gh))
        elif button == _win.mouse.RIGHT:
            self.gx = self.gx - self.gw / 2 + x * self.gw / self.w
            self.gy = self.gy - self.gh / 2 + y * self.gh / self.h
            self.gw /= self.zoom_valobj.value
            self.gh /= self.zoom_valobj.value
            self.set_graph_minmax()
            self.total_zoom /= (1 / self.zoom_valobj.value) ** 2
            #print('zoomed to %.5f,%.5f with size %.9f,%.9f' % (self.gx, self.gy, self.gw, self.gh))
        elif button == _win.mouse.MIDDLE:
            self.drag = False
            msx1, msy1 = self.on_plot(self.mdownx, self.mdowny)
            msx2, msy2 = self.on_plot(x, y)
            self.gx -= msx2 - msx1
            self.gy -= msy2 - msy1
            self.set_graph_minmax()
            self.offsx = 0
            self.offsy = 0
        self.render()

    def key_down(self, symbol, modifiers):
        if symbol == _win.key.LEFT:
            self.left()
        elif symbol == _win.key.RIGHT:
            self.right()
        elif symbol == _win.key.UP:
            self.up()
        elif symbol == _win.key.DOWN:
            self.down()


class Screen3D(Screen):
    def __init__(self, x, y, width, height, camera, rotation, offset, valset, bg=(0, 0, 0), visible=True, active=True):
        self.camera = camera
        self.rotation = rotation
        self.offset = offset
        super().__init__(x, y, width, height, valset, bg, visible, active)

    def set_bg(self, color):
        pass

    def draw(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        ar = self.w / self.h
        gluPerspective(60, ar, .01, 10000)
        glMatrixMode(GL_MODELVIEW)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_SCISSOR_TEST)
        glScissor(int(self.x), int(self.y), int(self.x + self.w), int(self.y + self.h))

        glPushMatrix()

        '''
        Walk view
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 1)
        glTranslatef(*self.camera)
        glTranslatef(*self.offset)
        '''

        # Centered view
        # dist has to be z value ???
        glTranslatef(*self.camera)
        glTranslatef(*self.offset)
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 1)

        self._batch.draw()

        glPopMatrix()

        glDisable(GL_SCISSOR_TEST)
        glDisable(GL_DEPTH_TEST)

    def add_point(self, x, y, z, color=(255, 255, 255)):
        self._vertexes['points'].extend((x, y, z))
        self._colors['points'].extend(color)

    def add_points(self, points, colors):
        self._vertexes['points'].extend(points)
        self._colors['points'].extend(colors)

    def add_line(self, x1, y1, z1, x2, y2, z2, color=(255, 255, 255)):
        self._vertexes['lines'].extend((x1, y1, z1, x2, y2, z2))
        self._colors['lines'].extend(color * 2)

    def set_line_strip(self, lines, colors):
        self._vertexes['line_strip'] = lines
        self._colors['line_strip'] = colors

    def add_triangle(self, x1, y1, z1, x2, y2, z2, x3, y3, z3, color=(255, 255, 255), uniform=True, colors=([255] * 9)):
        self._vertexes['triangles'].extend((x1, y1, z1, x2, y2, z2, x3, y3, z3))
        if uniform:
            self._colors['triangles'].extend(color * 3)
        else:
            self._colors['triangles'].extend(colors)

    def add_quad(self, x1, y1, z1, x2, y2, z2, x3, y3, z3, x4, y4, z4, color=(255, 255, 255), uniform=True, colors=([255] * 12)):
        self._vertexes['quads'].extend((x1, y1, z1, x2, y2, z2, x3, y3, z3, x4, y4, z4))
        if uniform:
            self._colors['quads'].extend(color * 4)
        else:
            self._colors['quads'].extend(colors)

    def key_down(self, symbol, modifiers):
        if symbol == _win.key.LEFT:
            self.rotation[1] += 5
        elif symbol == _win.key.RIGHT:
            self.rotation[1] -= 5
        elif symbol == _win.key.UP:
            self.rotation[0] += 5
        elif symbol == _win.key.DOWN:
            self.rotation[0] -= 5
        elif symbol == _win.key.X:
            self.rotation[2] -= 5
        elif symbol == _win.key.Z:
            self.rotation[2] += 5
        elif symbol == _win.key.S:
            self.offset[2] += 10
        elif symbol == _win.key.A:
            self.offset[2] -= 10
