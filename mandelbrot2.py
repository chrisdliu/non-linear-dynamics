from pyg import *
import time

class Mandelbrot(Window):
    def setvars(self):
        self.stepx = .005
        self.stepy = .005
        self.offsx = 0
        self.offsy = 0

    def load(self):
        self.batch.add(2, GL_LINES, None, ('v3f', (300 - self.offsx / self.stepx, 200, -1, 300 - self.offsx / self.stepx, 800, -1)), ('c3B', (255, 255, 255, 255, 255, 255)))
        self.batch.add(2, GL_LINES, None, ('v3f', (0, 500 + self.offsy / self.stepy, -1, 600, 500 + self.offsy / self.stepy, -1)), ('c3B', (255, 255, 255, 255, 255, 255)))

        pallet = []
        max_i = 20
        for i in range(max_i):
            pallet.append(i * 10)

        points = []
        colors = []

        ctotal = 0
        for x in range(-300, 301):
            for y in range(-300, 301):
                cstart = time.time()
                sx = x * self.stepx + self.offsx
                sy = y * self.stepy + self.offsy
                cx = 0
                cy = 0
                i = -1 #range 0 to max_i - 1
                cx2 = cx*cx
                cy2 = cy*cy
                while cx2 + cy2 < 4 and i < max_i - 1:
                    cy = (cx+cy)*(cx+cy) - cx2 - cy2
                    cy += sy
                    cx = cx2 - cy2 + sx
                    cx2 = cx*cx
                    cy2 = cy*cy
                    i += 1
                cend = time.time()
                ctotal += cend - cstart
                if i > 0:
                    px = x + 300
                    py = y + 500
                    points.append(px)
                    points.append(py)
                    color = pallet[i]
                    colors.append(color)
                    colors.append(0)
                    colors.append(0)
        print(ctotal)
        print(len(points))
        print(len(colors))
        self.batch.add(len(points)//2, GL_POINTS, None, ('v2i', points), ('c3B', colors))

window = Mandelbrot(width=600, height=800, caption='NLD', resizable=False)
glClearColor(0, 0, 0, 1)
pyglet.app.run()
