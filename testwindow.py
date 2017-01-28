import pyglet
import pyg
import numpy as np
import ctypes

class TestScreen(pyg.screen.Screen3D):
    def render(self):
        #self.add_line(100, 100, 200, 200, color=(255, 0, 0))
        #self.add_triangle(300, 100, 400, 100, 350, 200, uniform=False, colors=(255, 0, 0, 0, 255, 0, 0, 0, 255))
        #self.add_quad(400, 400, 450, 400, 475, 450, 350, 500, uniform=False, colors=(235, 68, 90, 22, 74, 63, 54, 101, 251, 98, 155, 33))
        #self.flush()

        #self.img1 = pyglet.image.AbstractImage(20, 40).get_image_data()
        #self.img1 = pyglet.image.ImageData(20, 40, 'RGB', np.array([255, 0, 0] * 20 * 40, dtype=np.ubyte).ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte)))
        #self.img2 = pyglet.image.ImageData(20, 40, 'RGB',
        #                                   np.array([0, 0, 255] * 20 * 40, dtype=np.ubyte).ctypes.data_as(
        #                                       ctypes.POINTER(ctypes.c_ubyte)))
        #print(self.img1.get_data('RGB', 20 * 3) == self.img2.get_data('RGB', 20 * 3))
        #print(self.img1.get_data('RGB', 20 * 3)[0:10])
        #print(self.img2.get_data('RGB', 20 * 3)[0:10])
        #self.img1.
        #self.img1 = pyglet.image.Texture(20, 40, pyglet.gl.GL_TEXTURE_2D, 1)
        #self.img1data = self.img1.get_image_data()
        #self.img1data.set_data('RGB', 20 * 3, np.array([255, 0, 0] * 20 * 40, dtype=np.ubyte).ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte)))
        #print(type(self.img1data.get_data('RGB', 20 * 3)))
        pass

    def resize(self, width, height):
        self.w = width
        self.h = height - 200


class TestWindow(pyg.window.Window):
    def set_vars(self):
        #self.valset.add_value('val', 1)
        self.add_screen('main', (TestScreen(0, 200, 600, 600, self.valset, bg=(255, 255, 255))))
        #self.add_int_slider('valslider', 100, 100, 100, 20, 20, 'Val', self.valset.get_obj('val'), -5, 2)

    def mouse_up(self, x, y, buttons, modifiers):
        self.render()


window = TestWindow(width=600, height=800, caption='Logistics Graph', bg=(0, 0, 0, 1), resizable=True)
pyglet.app.run()
