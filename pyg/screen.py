import pyglet.gl as gl
import pyglet.graphics as graphics
import pyglet.window as win


class ScreenGroup(graphics.OrderedGroup):
    def __init__(self, x, y, w, h, order, offsx=0, offsy=0, parent=None):
        super().__init__(order, parent=parent)
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.offsx = offsx
        self.offsy = offsy

    def set_state(self):
        """
        Enables a scissor test on the region and translates the screen based on its offset
        """
        gl.glTranslatef(self.x + self.offsx + .5, self.y + self.offsy + .5, 0)
        gl.glPushAttrib(gl.GL_ENABLE_BIT | gl.GL_TRANSFORM_BIT | gl.GL_CURRENT_BIT)
        self.was_scissor_enabled = gl.glIsEnabled(gl.GL_SCISSOR_TEST)
        gl.glEnable(gl.GL_SCISSOR_TEST)
        gl.glScissor(int(self.x), int(self.y), int(self.w), int(self.h))

    def unset_state(self):
        """
        Disables the scissor test and translates the screen based on its offset
        """
        if not self.was_scissor_enabled:
            gl.glDisable(gl.GL_SCISSOR_TEST)
        gl.glPopAttrib()
        gl.glTranslatef(-(self.x + self.offsx + .5), -(self.y + self.offsy + .5), 0)


class Screen:
    _vertex_types = ('points', 'lines', 'line_strip', 'triangles', 'quads')

    def __init__(self, x, y, width, height, valset, bg=(255, 255, 255), visible=True, active=True):
        self.x = x
        self.y = y
        self.w = width
        self.h = height
        self.visible = visible
        self.active = active

        self.batch = graphics.Batch()
        self._group = ScreenGroup(x, y, width, height, 0)
        self._bg_group = ScreenGroup(x, y, width, height, -1)
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

    def set_visible(self, visible):
        """
        Sets screen.visible
        if True, renders the screen
        if False, deletes the screen's vertex lists
        :param visible: screen visible
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
        :param active: screen active
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

    def set_bg(self, color):
        """
        Sets the screen's background color
        :param color: background color
        """
        self.bg = color
        if self._vertex_lists['bg']:
            self._vertex_lists['bg'].delete()
            self._vertex_lists['bg'] = None
        if self.visible:
            self._vertex_lists['bg'] = self.batch.add(4, gl.GL_QUADS, self._bg_group,
                                                      ('v2f', (0, 0, 0, self.h, self.w, self.h, self.w, 0)),
                                                      ('c3B', color * 4))

    def add_point(self, x, y, z=0, color=(0, 0, 0)):
        self._vertexes['points'].extend((x, y, z))
        self._colors['points'].extend(color)

    def add_points(self, points, colors):
        self._vertexes['points'].extend(points)
        self._colors['points'].extend(colors)

    def set_points_both(self, points, colors):
        self._vertexes['points'] = points
        self._colors['points'] = colors

    def add_line(self, x1, y1, x2, y2, z=0, color=(0, 0, 0)):
        self._vertexes['lines'].extend((x1, y1, z, x2, y2, z))
        self._colors['lines'].extend(color * 2)

    def set_lines_both(self, lines, colors):
        self._vertexes['lines'] = lines
        self._colors['lines'] = colors

    def set_line_strip(self, lines, colors):
        self._vertexes['line_strip'] = lines
        self._colors['line_strip'] = colors

    def add_triangle(self, x1, y1, x2, y2, x3, y3, z=0, color=(0, 0, 0), uniform=True, colors=((0,) * 9)):
        self._vertexes['triangles'].extend((x1, y1, z, x2, y2, z, x3, y3, z))
        if uniform:
            self._colors['triangles'].extend(color * 3)
        else:
            self._colors['triangles'].extend(colors)

    def add_quad(self, x1, y1, x2, y2, x3, y3, x4, y4, z=0, color=(0, 0, 0), uniform=True, colors=((0,) * 12)):
        self._vertexes['quads'].extend((x1, y1, z, x2, y2, z, x3, y3, z, x4, y4, z))
        if uniform:
            self._colors['quads'].extend(color * 4)
        else:
            self._colors['quads'].extend(colors)

    def flush(self):
        """
        Deletes the current vertex lists
        If the screen is visible, adds the vertexes in the buffer to the batch
        Clears the buffer
        """
        if not self._vertex_lists['bg']:
            self._vertex_lists['bg'] = self.batch.add(4, gl.GL_QUADS, self._bg_group,
                                                      ('v2f', (0, 0, 0, self.h, self.w, self.h, self.w, 0)),
                                                      ('c3B', self.bg * 4))
        for vtype in self._vertex_types:
            if self._vertex_lists[vtype]:
                self._vertex_lists[vtype].delete()
                self._vertex_lists[vtype] = None
            vlist = None
            if not self.visible:
                continue
            if vtype == 'points':
                vlist = self.batch.add(len(self._vertexes[vtype]) // 3, gl.GL_POINTS, self._group, ('v3f', self._vertexes[vtype]), ('c3B', self._colors[vtype]))
            elif vtype == 'lines':
                vlist = self.batch.add(len(self._vertexes[vtype]) // 3, gl.GL_LINES, self._group, ('v3f', self._vertexes[vtype]), ('c3B', self._colors[vtype]))
            elif vtype == 'line_strip':
                vlist = self.batch.add(len(self._vertexes[vtype]) // 2, gl.GL_LINE_STRIP, self._group, ('v2f', self._vertexes[vtype]), ('c3B', self._colors[vtype]))
            elif vtype == 'triangles':
                vlist = self.batch.add(len(self._vertexes[vtype]) // 3, gl.GL_TRIANGLES, self._group, ('v3f', self._vertexes[vtype]), ('c3B', self._colors[vtype]))
            elif vtype == 'quads':
                vlist = self.batch.add(len(self._vertexes[vtype]) // 3, gl.GL_QUADS, self._group, ('v3f', self._vertexes[vtype]), ('c3B', self._colors[vtype]))
            self._vertex_lists[vtype] = vlist

        self.clear_buffer()

    def clear_buffer(self):
        """
        Clears the buffer arrays
        """
        for vtype in self._vertex_types:
            self._vertexes[vtype] = []
            self._colors[vtype] = []

    def draw(self):
        self.batch.draw()

    def is_inside(self, x, y):
        """
        Returns if x, y is inside the screen
        :param x: x
        :param y: y
        """
        return 0 <= x - self.x < self.w and 0 <= y - self.y < self.h

    def on_resize(self, width, height):
        self.resize(width, height)
        self._group.w = self.w
        self._group.h = self.h
        self._bg_group.w = self.w
        self._bg_group.h = self.h
        self.set_bg(self.bg)

    def set_pos(self, x, y):
        """
        Sets the screen's position
        :param x: x
        :param y: y
        """
        self.x = x
        self.y = y
        self._group.x = x
        self._group.y = y
        self._bg_group.x = x
        self._bg_group.y = y

    # to be overriden
    # render should add points, then flush to the batch
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


class GraphScreen(Screen):
    def __init__(self, x, y, width, height, gx, gy, gw, gh, valset, zoom_valobj, bg=(255, 255, 255), visible=True, active=True):
        super().__init__(x, y, width, height, valset, bg=bg, visible=visible, active=active)
        self._ow = width
        self._oh = height
        self.set_graph_coords(gx, gy, gw, gh)
        self.set_graph_minmax()
        self.reset_to(gx, gy, gw, gh)

        self.zoom_valobj = zoom_valobj
        self.total_zoom = 1
        self.drag = False
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

    def resize(self, new_width, new_height):
        """
        Resizes the screen based on the window's new width and height
        Should be overritten if screen does not take up entire window
        :param width: new window width
        :param height: new window height
        """
        self.refit(new_width, new_height)

    def refit(self, new_width, new_height):
        """
        Sets the screen's width and height and changes the graph's width and height accordingly
        :param new_width: new screen width
        :param new_height: new screen height
        """
        old_gw = self.gw
        old_gh = self.gh
        self.gw *= new_width / self.w
        self.gh *= new_height / self.h
        self.set_graph_minmax()
        self.total_zoom *= (old_gw * old_gh) / (self.gw * self.gh)
        self.w = new_width
        self.h = new_height

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

    def draw(self):
        """
        Translates by the drag, draws, and translates back
        """
        gl.glTranslatef(self.offsx, self.offsy, 0)
        self.batch.draw()
        gl.glTranslatef(-self.offsx, -self.offsy, 0)

    def mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.drag:
            self.offsx = x - self.mdownx
            self.offsy = y - self.mdowny
            self._bg_group.offsx = -self.offsx
            self._bg_group.offsy = -self.offsy

    def mouse_down(self, x, y, button, modifier):
        if button == win.mouse.MIDDLE:
            self.drag = True
            self.mdownx = x
            self.mdowny = y

    def mouse_up(self, x, y, button, modifiers):
        if button == win.mouse.LEFT:
            self.gx = self.gx - self.gw / 2 + x * self.gw / self.w
            self.gy = self.gy - self.gh / 2 + y * self.gh / self.h
            self.gw *= self.zoom_valobj.value
            self.gh *= self.zoom_valobj.value
            self.set_graph_minmax()
            self.total_zoom *= (1 / self.zoom_valobj.value) ** 2
            #print('zoomed to %.5f,%.5f with size %.9f,%.9f' % (self.gx, self.gy, self.gw, self.gh))
        elif button == win.mouse.RIGHT:
            self.gx = self.gx - self.gw / 2 + x * self.gw / self.w
            self.gy = self.gy - self.gh / 2 + y * self.gh / self.h
            self.gw /= self.zoom_valobj.value
            self.gh /= self.zoom_valobj.value
            self.set_graph_minmax()
            self.total_zoom /= (1 / self.zoom_valobj.value) ** 2
            #print('zoomed to %.5f,%.5f with size %.9f,%.9f' % (self.gx, self.gy, self.gw, self.gh))
        elif button == win.mouse.MIDDLE:
            self.drag = False
            msx1, msy1 = self.on_plot(self.mdownx, self.mdowny)
            msx2, msy2 = self.on_plot(x, y)
            self.gx -= msx2 - msx1
            self.gy -= msy2 - msy1
            self.set_graph_minmax()
            self.offsx = 0
            self.offsy = 0
            self._bg_group.offsx = 0
            self._bg_group.offsy = 0
        self.render()

    def key_down(self, symbol, modifiers):
        if symbol == win.key.LEFT:
            self.left()
        elif symbol == win.key.RIGHT:
            self.right()
        elif symbol == win.key.UP:
            self.up()
        elif symbol == win.key.DOWN:
            self.down()
