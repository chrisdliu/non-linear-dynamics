from tkg import *
import time

class Mandelbrot(Viewer):
    def setvars(self):
        self.stepx = .005
        self.stepy = .005
        self.offsx = 0
        self.offsy = 0

    def draw(self):
        self.canvas.create_rectangle(0, 0, 600, 600, fill='white')
        self.canvas.create_line(300 - self.offsx / self.stepx, 0, 300 - self.offsx / self.stepx, 600, fill='black')
        self.canvas.create_line(0, 300 + self.offsy / self.stepy, 600, 300 + self.offsy / self.stepy, fill='black')
        pallet = []
        max_i = 20
        for i in range(max_i):
            r = str(hex(int(i * 10)))[2:]
            if len(r) == 1: r = '0' + r
            pallet.append('#%s0000' % r)

        ptotal = 0
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
                #if i == max_i:
                px = x + 300
                py = -y + 300
                pstart = time.time()
                self.canvas.create_rectangle(px, py, px, py, fill=pallet[i], outline='')
                pend = time.time()
                ptotal += pend - pstart
        print(ctotal)
        print(ptotal)

    def up(self):
        self.offsy += 0.4
        self.draw()

    def down(self):
        self.offsy -= 0.4
        self.draw()

    def left(self):
        self.offsx -= 0.4
        self.draw()

    def right(self):
        self.offsx += 0.4
        self.draw()

    def zoom_in(self):
        self.stepx *= 0.8
        self.stepy *= 0.8
        self.draw()

    def zoom_out(self):
        self.stepx *= 1.25
        self.stepy *= 1.25
        self.draw()


app = Window(title='Mandelbrot', size=(600, 800), frameclasses=(Mandelbrot,))
app.mainloop()