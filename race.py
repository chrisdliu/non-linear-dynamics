from pyg import *
from PIL import Image

def surrounding(pos):
    p = []
    for x in range(-1, 2):
        for y in range(-1, 2):
            if x == pos[0] and y == pos[1]:
                continue
            p.append((pos[0] + x, pos[1] + y))
    return p


class Block():
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type #0 - empty; 1 - wall; 2 - start; 3 - finish
        self.heuristic = {}

    def pos(self):
        return (self.x, self.y)


class Race(Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loadmap('map.png')

    def loadmap(self, filepath):
        try:
            mapimg = Image.open('map.png')
        except:
            self.mode = -1
            return
        size = mapimg.size
        pixels = mapimg.load()
        self.gridw = size[0]
        self.gridh = size[1]
        self.grid = []
        pallet = {
            (255, 255, 255): 0,
            (0, 0, 0): 1,
            (0, 255, 0): 2,
            (255, 0, 0): 3
        }
        self.startpoints = []
        self.endpoints = []
        for x in range(self.gridw):
            column = []
            for y in range(self.gridh - 1, -1, -1):
                color = pixels[x,y]
                if color in pallet:
                    column.append(Block(x, -y + self.gridh - 1, pallet[color]))
                    if column[-1].type == 2:
                        self.startpoints.append((x, -y + self.gridh - 1))
                    if column[-1].type == 3:
                        self.endpoints.append((x, -y + self.gridh - 1))
                else:
                    column.append(Block(x, -y + self.gridh - 1, 1))
            self.grid.append(column)
        self.distgrid = [[-1 for i in range(self.gridh)] for j in range(self.gridw)]
        for x in range(self.gridw):
            for y in range(self.gridh):
                if self.grid[x][y].type in (0, 2):
                    self.distgrid[x][y] = 0
        self.setdistgrid()
        self.renderscreen()

    def in_grid(self, pos):
        return not (pos[0] < 0 or pos[0] >= self.gridw or pos[1] < 0 or pos[1] >= self.gridh)

    def fulldistgrid(self):
        for x in range(self.gridw):
            for y in range(self.gridh):
                if self.distgrid[x][y] == 0:
                    return False
        return True

    def setdistgrid(self, d=1):
        if d == 1:
            for endp in self.endpoints:
                s = surrounding(endp)
                for sp in s:
                    if not self.in_grid(sp):
                        continue
                    if self.distgrid[sp[0]][sp[1]] == 0:
                        self.distgrid[sp[0]][sp[1]] = 1
        else:
            dlist = []
            for x in range(self.gridw):
                for y in range(self.gridh):
                    if self.distgrid[x][y] == d - 1:
                        dlist.append((x, y))
            for dp in dlist:
                s = surrounding(dp)
                for sp in s:
                    if not self.in_grid(sp):
                        continue
                    if self.distgrid[sp[0]][sp[1]] == 0:
                        self.distgrid[sp[0]][sp[1]] = d
        if not self.fulldistgrid():
            self.setdistgrid(d=d + 1)


    def setvars(self):
        self.vertex_lists = []
        self.overlay = None
        self.grid = None
        self.gridw = 0
        self.gridh = 0
        self.offsx = 0
        self.offsy = 0
        self.mode = 0 #0 - regular; 1 - distance from finish; -1 - can't load image

    def up(self):
        self.offsy += 1
        self.renderscreen()

    def down(self):
        self.offsy -= 1
        self.renderscreen()

    def left(self):
        self.offsx -= 1
        self.renderscreen()

    def right(self):
        self.offsx += 1
        self.renderscreen()
    
    def up5(self):
        self.offsy += 5
        self.renderscreen()

    def down5(self):
        self.offsy -= 5
        self.renderscreen()

    def left5(self):
        self.offsx -= 5
        self.renderscreen()

    def right5(self):
        self.offsx += 5
        self.renderscreen()

    def setmode(self, m):
        self.mode = m
        self.renderscreen()

    def render(self):
        upb = Button(75, 145, 40, 40, 'Up', self.up)
        self.buttons.append(upb)
        downb = Button(75, 100, 40, 40, 'Down', self.down)
        self.buttons.append(downb)
        leftb = Button(30, 120, 40, 40, 'Left', self.left)
        self.buttons.append(leftb)
        rightb = Button(120, 120, 40, 40, 'Right', self.right)
        self.buttons.append(rightb)
        up5b = Button(220, 145, 40, 40, 'Up 5', self.up5)
        self.buttons.append(up5b)
        down5b = Button(220, 100, 40, 40, 'Down 5', self.down5)
        self.buttons.append(down5b)
        left5b = Button(175, 120, 40, 40, 'Left 5', self.left5)
        self.buttons.append(left5b)
        right5b = Button(265, 120, 40, 40, 'Right 5', self.right5)
        self.buttons.append(right5b)
        run = Button(350, 120, 40, 40, 'Run', None)
        self.buttons.append(run)
        m0 = Button(350, 60, 40, 40, 'Mode 0', lambda: self.setmode(0))
        self.buttons.append(m0)
        m1 = Button(400, 60, 40, 40, 'Mode 1', lambda: self.setmode(1))
        self.buttons.append(m1)
        self.load_buttons()

    def renderscreen(self):
        for vlist in self.vertex_lists:
            vlist.delete()
            self.vertex_lists.remove(vlist)
        if self.mode == 0:
            quads = []
            colors = []
            pallet = {
                0: (150, 150, 150),
                1: (30, 30, 30),
                2: (0, 240, 0),
                3: (240, 0, 0)
            }
            for x in range(self.offsx, self.offsx + 60):
                if x < 0 or x >= self.gridw:
                    continue
                for y in range(self.offsy, self.offsy + 60):
                    if y < 0 or y >= self.gridh:
                        continue
                    px = (x - self.offsx) * 10
                    py = (y - self.offsy) * 10 + 200
                    points = [ px, py, px + 10, py, px + 10, py + 10, px, py + 10 ]
                    for point in points:
                        quads.append(point)
                    rgb = pallet[self.grid[x][y].type]
                    for i in range(4):
                        for color in rgb:
                            colors.append(color)

            self.vertex_lists.append(self.batch.add(len(quads)//2, GL_QUADS, None, ('v2f', quads), ('c3B', colors)))
        elif self.mode == 1:
            quads = []
            colors = []
            pallet = {
                0: (150, 150, 150),
                1: (30, 30, 30),
                2: (0, 240, 0),
                3: (240, 0, 0)
            }
            for x in range(self.offsx, self.offsx + 60):
                if x < 0 or x >= self.gridw:
                    continue
                for y in range(self.offsy, self.offsy + 60):
                    if y < 0 or y >= self.gridh:
                        continue
                    px = (x - self.offsx) * 10
                    py = (y - self.offsy) * 10 + 200
                    points = [ px, py, px + 10, py, px + 10, py + 10, px, py + 10 ]
                    for point in points:
                        quads.append(point)
                    rgb = pallet[self.grid[x][y].type]
                    if self.grid[x][y].type in (0, 2):
                        rgb = [240 - 30 * self.distgrid[x][y], 240 - 30 * self.distgrid[x][y], 240 - 30 * self.distgrid[x][y]]
                    for i in range(4):
                        for color in rgb:
                            colors.append(color)

            self.vertex_lists.append(self.batch.add(len(quads)//2, GL_QUADS, None, ('v2f', quads), ('c3B', colors)))


    def renderoverlay(self):
        if self.overlay:
            self.overlay.delete()
        #self.overlay = self.batch.add(4, GL_QUADS, None, ('v3f', (100, 500, 1, 120, 500, 1, 120, 520, 1, 100, 520, 1)))


window = Race(width=600, height=800, caption='Race', resizable=True)
glClearColor(0, 0, 0, 1)
pyglet.app.run()
