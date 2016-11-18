import pyglet.gl as gl
import pyglet.window as win
import pyglet.graphics as graphics


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
        Enables a scissor test on the region
        """
        gl.glTranslatef(self.x + self.offsx + .5, self.y + self.offsy + .5, 0)
        gl.glPushAttrib(gl.GL_ENABLE_BIT | gl.GL_TRANSFORM_BIT | gl.GL_CURRENT_BIT)
        self.was_scissor_enabled = gl.glIsEnabled(gl.GL_SCISSOR_TEST)
        gl.glEnable(gl.GL_SCISSOR_TEST)
        gl.glScissor(int(self.x), int(self.y), int(self.w), int(self.h))

    def unset_state(self):
        """
        Disables the scissor test
        """
        if not self.was_scissor_enabled:
            gl.glDisable(gl.GL_SCISSOR_TEST)
        gl.glPopAttrib()
        gl.glTranslatef(-(self.x + self.offsx + .5), -(self.y + self.offsy + .5), 0)


class Screen:
    def __init__(self, x, y, width, height, bg=(255, 255, 255), valset=None, visible=True, active=True):
        self.x = x
        self.y = y
        self.w = width
        self.h = height
        self.visible = visible
        self.active = active

        self.batch = graphics.Batch()
        self.group = ScreenGroup(x, y, width, height, 0)
        self.bg_group = ScreenGroup(x, y, width, height, -1)
        self.vertex_lists = {}
        self.vertexes = {}
        self.colors = {}
        self.vertex_types = ('points', 'lines', 'triangles', 'quads')
        for type in self.vertex_types:
            self.vertex_lists[type] = None
            self.vertexes[type] = []
            self.colors[type] = []

        self.bg = bg
        self.set_bg(bg)

        self.valset = valset

    def set_visible(self, visible):
        self.visible = visible
        if visible:
            self.render()
        else:
            for type in self.vertex_lists.keys():
                if self.vertex_lists[type]:
                    self.vertex_lists[type].delete()
                self.vertex_lists[type] = None

    def get_val(self, name):
        return self.valset.get_val(name)

    def set_val(self, name, value):
        self.valset.set_val(name, value)

    def get_obj(self, name):
        return self.valset.get_obj(name)

    def set_bg(self, color):
        if 'bg' not in self.vertex_lists.keys():
            self.vertex_lists['bg'] = None
        if self.vertex_lists['bg']:
            self.vertex_lists['bg'].delete()
        if self.visible:
            self.vertex_lists['bg'] = self.batch.add(4, gl.GL_QUADS, self.bg_group,
                ('v2f', (0, 0, 0, self.h, self.w, self.h, self.w, 0)),
                ('c3B', color * 4))

    def add_point(self, x, y, z=0, color=(0, 0, 0)):
        self.vertexes['points'].extend((x, y, z))
        self.colors['points'].extend(color)

    def add_points(self, points, colors):
        self.vertexes['points'].extend(points)
        self.colors['points'].extend(colors)

    def set_points_both(self, points, colors):
        self.vertexes['points'] = points
        self.colors['points'] = colors

    def set_points_points(self, points):
        self.vertexes['points'] = points

    def set_points_colors(self, colors):
        self.colors['points'] = colors

    def add_line(self, x1, y1, x2, y2, z=0, color=(0, 0, 0)):
        self.vertexes['lines'].extend((x1, y1, z, x2, y2, z))
        self.colors['lines'].extend(color * 2)

    def set_lines_both(self, lines, colors):
        self.vertexes['lines'] = lines
        self.colors['lines'] = colors

    def add_triangle(self, x1, y1, x2, y2, x3, y3, z=0, color=(0, 0, 0), uniform=True, colors=((0,) * 9)):
        self.vertexes['triangles'].extend((x1, y1, z, x2, y2, z, x3, y3, z))
        if uniform:
            self.colors['triangles'].extend(color * 3)
        else:
            self.colors['triangles'].extend(colors)

    def add_quad(self, x1, y1, x2, y2, x3, y3, x4, y4, z=0, color=(0, 0, 0), uniform=True, colors=((0,) * 12)):
        self.vertexes['quads'].extend((x1, y1, z, x2, y2, z, x3, y3, z, x4, y4, z))
        if uniform:
            self.colors['quads'].extend(color * 4)
        else:
            self.colors['quads'].extend(colors)

    # add the other primitives

    def flush(self):
        for type in self.vertex_types:
            if self.vertex_lists[type]:
                self.vertex_lists[type].delete()
                self.vertex_lists[type] = None
            vlist = None
            if not self.visible:
                continue
            if type == 'points':
                vlist = self.batch.add(len(self.vertexes[type]) // 3, gl.GL_POINTS, self.group, ('v3f', self.vertexes[type]), ('c3B', self.colors[type]))
            elif type == 'lines':
                vlist = self.batch.add(len(self.vertexes[type]) // 3, gl.GL_LINES, self.group, ('v3f', self.vertexes[type]), ('c3B', self.colors[type]))
            elif type == 'triangles':
                vlist = self.batch.add(len(self.vertexes[type]) // 3, gl.GL_TRIANGLES, self.group, ('v3f', self.vertexes[type]), ('c3B', self.colors[type]))
            elif type == 'quads':
                vlist = self.batch.add(len(self.vertexes[type]) // 3, gl.GL_QUADS, self.group, ('v3f', self.vertexes[type]), ('c3B', self.colors[type]))
            self.vertex_lists[type] = vlist

        self.clear_buffer()

    def clear_buffer(self):
        for type in self.vertex_types:
            self.vertexes[type] = []
            self.colors[type] = []

    def on_draw(self):
        self.batch.draw()

    def is_inside(self, x, y):
        return 0 <= x - self.x < self.w and 0 <= y - self.y < self.h

    def on_resize(self, width, height):
        self.resize(width, height)
        self.group.w = self.w
        self.group.h = self.h
        self.bg_group.w = self.w
        self.bg_group.h = self.h
        self.set_bg(self.bg)

    def set_pos(self, x, y):
        self.x = x
        self.y = y
        self.group.x = x
        self.group.y = y
        self.bg_group.x = x
        self.bg_group.y = y

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
    def __init__(self, x, y, width, height, sx, sy, sw, sh, bg=(255, 255, 255), valset=None, visible=True):
        super().__init__(x, y, width, height, bg=bg, valset=valset, visible=visible)
        self._ow = width
        self._oh = height
        self.sx = sx
        self.sy = sy
        self.sw = sw
        self.sh = sh
        self._osx = sx
        self._osy = sy
        self._osw = sw
        self._osh = sh
        self.drag = False
        self.offsx = 0
        self.offsy = 0

    def reset(self):
        self.reset_graph()
        self.render()

    def reset_graph(self):
        '''
        self.sx = .5
        self.sy = .5
        self.sw = 1 * (self.w / self._ow)
        self.sh = 1 * (self.h / self._oh)
        '''
        self.sx = self._osx
        self.sy = self._osy
        self.sw = self._osw * (self.w / self._ow)
        self.sh = self._osh * (self.h / self._oh)

    def reset_to(self, sx, sy, sw, sh):
        self._osx = sx
        self._osy = sy
        self._osw = sw
        self._osh = sh

    def up(self):
        self.sy += self.sh / 5
        self.render()

    def down(self):
        self.sy -= self.sh / 5
        self.render()

    def left(self):
        self.sx -= self.sw / 5
        self.render()

    def right(self):
        self.sx += self.sw / 5
        self.render()

    def on_screen(self, x, y):
        return (x - self.sx + self.sw / 2) * self.w / self.sw, (y - self.sy + self.sh / 2) * self.h / self.sh

    def on_plot(self, px, py):
        return px * self.sw / self.w + self.sx - self.sw / 2, py * self.sh / self.h + self.sy - self.sh / 2

    def on_draw(self):
        gl.glTranslatef(self.offsx, self.offsy, 0)
        self.batch.draw()
        gl.glTranslatef(-self.offsx, -self.offsy, 0)

    def mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.drag:
            self.offsx = x - self.mdownx
            self.offsy = y - self.mdowny
            self.bg_group.offsx = -self.offsx
            self.bg_group.offsy = -self.offsy

    def mouse_down(self, x, y, button, modifier):
        if button == win.mouse.MIDDLE:
            self.drag = True
            self.mdownx = x
            self.mdowny = y

    def mouse_up(self, x, y, button, modifiers):
        if button == win.mouse.LEFT:
            self.sx = self.sx - self.sw / 2 + x * self.sw / self.w
            self.sy = self.sy - self.sh / 2 + y * self.sh / self.h
            self.sw *= self.get_val('sz')
            self.sh *= self.get_val('sz')
            print('zoomed to %.5f,%.5f with size %.9f,%.9f' % (self.sx, self.sy, self.sw, self.sh))
        elif button == win.mouse.RIGHT:
            self.sx = self.sx - self.sw / 2 + x * self.sw / self.w
            self.sy = self.sy - self.sh / 2 + y * self.sh / self.h
            self.sw /= self.get_val('sz')
            self.sh /= self.get_val('sz')
            print('zoomed to %.5f,%.5f with size %.9f,%.9f' % (self.sx, self.sy, self.sw, self.sh))
        elif button == win.mouse.MIDDLE:
            self.drag = False
            msx1, msy1 = self.on_plot(self.mdownx, self.mdowny)
            msx2, msy2 = self.on_plot(x, y)
            self.sx -= msx2 - msx1
            self.sy -= msy2 - msy1
            self.offsx = 0
            self.offsy = 0
            self.bg_group.offsx = 0
            self.bg_group.offsy = 0
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

    def resize(self, width, height):
        self.refit(width, height)

    def refit(self, new_width, new_height):
        self.sw *= new_width / self.w
        self.sh *= new_height / self.h
        self.w = new_width
        self.h = new_height
