"""
Deprecated
"""

import pyglet.graphics as graphics
from pyglet.gl import *


class ScreenGroup2D(graphics.OrderedGroup):
    def __init__(self, x, y, w, h, order, offsx=0, offsy=0, parent=None):
        super().__init__(order, parent=parent)
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.offsx = offsx
        self.offsy = offsy
        self.was_scissor_enabled = glIsEnabled(GL_SCISSOR_TEST)

    def set_state(self):
        """
        Enables a scissor test on the region and translates the screen based on its offset
        """

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.w, 0, self.h, -10, 10)
        glMatrixMode(GL_MODELVIEW)

        glTranslatef(self.x + self.offsx + .5, self.y + self.offsy + .5, 0)
        # ???
        #glPushAttrib(GL_ENABLE_BIT | GL_TRANSFORM_BIT | GL_CURRENT_BIT)
        glEnable(GL_DEPTH_TEST)
        self.was_scissor_enabled = glIsEnabled(GL_SCISSOR_TEST)
        glEnable(GL_SCISSOR_TEST)
        glScissor(int(self.x), int(self.y), int(self.x + self.w), int(self.y + self.h))

    def unset_state(self):
        """
        Disables the scissor test and translates the screen based on its offset
        """
        if not self.was_scissor_enabled:
            glDisable(GL_SCISSOR_TEST)
        #glPopAttrib()
        glTranslatef(-(self.x + self.offsx + .5), -(self.y + self.offsy + .5), 0)
        glDisable(GL_DEPTH_TEST)


class ScreenGroup3D(graphics.OrderedGroup):
    def __init__(self, x, y, w, h, camera, rotation, offset, order, parent=None):
        super().__init__(order, parent=parent)
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.camera = camera
        self.rotation = rotation
        self.offset = offset

    def set_state(self):
        '''
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_SCISSOR_TEST)
        glScissor(int(self.x), int(self.y), int(self.x + self.w), int(self.y + self.h))
        glPushMatrix()
        '''

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


    def unset_state(self):
        glPopMatrix()
        glDisable(GL_SCISSOR_TEST)
        glDisable(GL_DEPTH_TEST)
