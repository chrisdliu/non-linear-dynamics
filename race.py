from pyg import *
from PIL import Image
import math, time

def surrounding(pos):
    p = []
    for x in range(-1, 2):
        for y in range(-1, 2):
            if x == pos[0] and y == pos[1]:
                continue
            p.append((pos[0] + x, pos[1] + y))
    return p

def get_moves(pos):
    p = []
    for x in range(-1, 2):
        for y in range(-1, 2):
            p.append((pos[0] + pos[2] + x, pos[1] + pos[3] + y, pos[2] + x, pos[3] + y))
    return p

def has_node(pos, l):
    for node in l:
        if node.pos() == pos:
            return True
    return False

def get_node(pos, l):
    for node in l:
        if node.pos() == pos:
            return node
    return None

def a_dist(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def dist(pos1, pos2):
    return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

class Block():
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type #0 - empty; 1 - wall; 2 - start; 3 - finish
        self.heuristic = {}

    def pos(self):
        return (self.x, self.y)


class a_Node():
    def __init__(self, x, y, dx, dy, g, h, parent):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.g = g
        self.h = h
        self.parent = parent

    def pos(self):
        return (self.x, self.y, self.dx, self.dy)

    def f(self):
        return self.g + self.h


class Race(Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loadmap('map2.png')

    def loadmap(self, filepath):
        try:
            mapimg = Image.open(filepath)
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
        self.distgrid2 = [[-1 for i in range(self.gridh)] for j in range(self.gridw)]
        for x in range(self.gridw):
            for y in range(self.gridh):
                if self.grid[x][y].type in (0, 2):
                    self.distgrid[x][y] = 0
                    self.distgrid2[x][y] = 0
        self.setdistgrid()
        self.setdistgrid2()
        self.a_grid = [[None for i in range(self.gridh)] for j in range(self.gridw)]

        self.renderscreen()

        #debug section
        print(self.valid_move((26, 21), (27, 18)))


    def in_grid(self, pos):
        return not (pos[0] < 0 or pos[0] >= self.gridw or pos[1] < 0 or pos[1] >= self.gridh)

    def fulldistgrid(self):
        for x in range(self.gridw):
            for y in range(self.gridh):
                if self.distgrid[x][y] == 0:
                    return False
        return True

    def fulldistgrid2(self):
        for x in range(self.gridw):
            for y in range(self.gridh):
                if self.distgrid2[x][y] == 0:
                    return False
        return True

    #a* manhattan distance
    def setdistgrid(self):
        for x in range(self.gridw):
            for y in range(self.gridh):
                if self.distgrid[x][y] != 0:
                    continue
                dists = []
                for endp in self.endpoints:
                    dists.append(a_dist((x, y), endp))
                self.distgrid[x][y] = min(dists)


    #racetrack distance
    def setdistgrid2(self, d=1):
        if d == 1:
            for endp in self.endpoints:
                s = surrounding(endp)
                for sp in s:
                    if not self.in_grid(sp):
                        continue
                    if self.distgrid2[sp[0]][sp[1]] == 0:
                        self.distgrid2[sp[0]][sp[1]] = 1
        else:
            dlist = []
            for x in range(self.gridw):
                for y in range(self.gridh):
                    if self.distgrid2[x][y] == d - 1:
                        dlist.append((x, y))
            for dp in dlist:
                s = surrounding(dp)
                for sp in s:
                    if not self.in_grid(sp):
                        continue
                    if self.distgrid2[sp[0]][sp[1]] == 0:
                        self.distgrid2[sp[0]][sp[1]] = d
        if not self.fulldistgrid2():
            self.setdistgrid2(d=d + 1)


    def valid_move(self, pos1, pos2):
        if not self.in_grid(pos2):
            return False
        if self.grid[pos2[0]][pos2[1]].type == 1:
            return False
        dx = pos2[0] - pos1[0]
        dy = pos2[1] - pos1[1]
        if dx == 0 and dy == 0:
            return True
        if dx == 0:
            dys = dy // abs(dy)
            for i in range(1, dy * dys):
                if self.grid[pos1[0]][pos1[1] + i * dys].type == 1:
                    return False
            return True
        if dy == 0:
            dxs = dx // abs(dx)
            for i in range(1, dx * dxs):
                if self.grid[pos1[0] + i * dxs][pos1[1]].type == 1:
                    return False
            return True
        sx = dy / dx
        sy = dx / dy
        dxs = dx // abs(dx)
        dys = dy // abs(dy)
        for i in range(1, dx * dxs):
            y = pos1[1] + abs(i * sx) * dys
            y1 = math.floor(y)
            y2 = math.ceil(y)
            #print('testing: %d,%d and %d,%d' % ( pos1[0] + i * dxs, y1, pos1[0] + i * dxs, y2))
            if self.grid[pos1[0] + i * dxs][y1].type == 1 and self.grid[pos1[0] + i * dxs][y2].type == 1:
                return False
        for i in range(1, dy * dys):
            x = pos1[0] + abs(i * sy) * dxs
            x1 = math.floor(x)
            x2 = math.ceil(x)
            #print('testing: %d,%d and %d,%d' % ( x1, pos1[1] + i * dys, x2, pos1[1] + i * dys))
            if self.grid[x1][pos1[1] + i * dys].type == 1 and self.grid[x2][pos1[1] + i * dys].type == 1:
                return False
        return True

    #returns move if can end, None if can't end
    def can_end(self, pos):
        moves = get_moves(pos)
        for move in moves:
            if self.in_grid(move) and self.grid[move[0]][move[1]].type == 3:
                return move
            dx = move[2]
            dy = move[3]
            if dx == 0 and dy == 0:
                continue
            if dx == 0:
                dys = dy // abs(dy)
                for i in range(1, dy * dys):
                    gy = pos[1] + i * dys
                    if self.in_grid((pos[0], gy)) and self.grid[pos[0]][gy].type == 3:
                        return move
                continue
            if dy == 0:
                dxs = dx // abs(dx)
                for i in range(1, dx * dxs):
                    gx = pos[0] + i * dxs
                    if self.in_grid((gx, pos[1])) and self.grid[gx][pos[1]].type == 3:
                        return move
                continue
            sx = dy / dx
            sy = dx / dy
            dxs = dx // abs(dx)
            dys = dy // abs(dy)
            for i in range(1, dx * dxs):
                y = pos[1] + abs(i * sx) * dys
                y1 = math.floor(y)
                y2 = math.ceil(y)
                gx = pos[0] + i * dxs
                if self.in_grid((gx, y1)) and self.in_grid((gx, y2)) and self.grid[gx][y1].type == 3 and self.grid[gx][y2].type == 3:
                    return move
            for i in range(1, dy * dys):
                x = pos[0] + abs(i * sy) * dxs
                x1 = math.floor(x)
                x2 = math.ceil(x)
                gy = pos[1] + i * dys
                if self.in_grid((x1, gy)) and self.in_grid((x2, gy)) and self.grid[x1][gy].type == 1 and self.grid[x2][gy].type == 1:
                    return move
        return None

    def heuristic(self, pos):
        nx = pos[0] + pos[2]
        ny = pos[1] + pos[3]
        '''
        total = 0
        for endp in self.endpoints:
            total += dist((nx, ny), endp)
        return total / len(self.endpoints)
        '''
        x = pos[0]
        y = pos[1]
        return self.distgrid2[x][y] / (1 + math.sqrt(pos[2] **2 + pos[3] ** 2))


    ''' #a* run
    def run(self):
        self.setmode(0)
        movecost = .1
        totaltime = 0
        totals = time.time()
        for startp in self.startpoints[:1]:
            closedSet = []
            openSet = [a_Node(startp[0], startp[1], 0, 0, 0, self.heuristic((startp[0], startp[1], 0, 0)), None)]
            path = []
            endnode = None
            while len(openSet) > 0:
                c = openSet[0] #current
                openSet = openSet[1:]
                closedSet.append(c)
                ts = time.time()
                endmove = self.can_end(c.pos())
                if endmove and self.valid_move(c.pos(), endmove):
                    te = time.time()
                    totaltime += te - ts
                    print('found solution')
                    closedSet.append(a_Node(endmove[0], endmove[1], endmove[2], endmove[3], c.g + movecost, 0, c.pos()))
                    endnode = closedSet[-1]
                    break
                te = time.time()
                totaltime += te - ts
                moves = get_moves(c.pos())
                for move in moves:
                    if has_node(move, closedSet):
                        continue
                    ts = time.time()
                    if not self.valid_move(c.pos(), move):
                        te = time.time()
                        totaltime += te - ts
                        continue
                    te = time.time()
                    totaltime += te - ts
                    g = c.g + movecost
                    if has_node(move, openSet):
                        rnode = get_node(move, openSet) #revisited node
                        if g >= rnode.g:
                            continue #current path to rnode is best
                        rnode.parent = c.pos() #update with better path
                        rnode.g = g
                    else:
                        nnode = a_Node(move[0], move[1], move[2], move[3], g, self.heuristic(move), c.pos())
                        if len(openSet) == 0:
                            openSet.append(nnode)
                        else:
                            for i in range(len(openSet)):
                                if nnode.f() < openSet[i].f():
                                    openSet.insert(i, nnode)
                                    break
                                if i == len(openSet) - 1:
                                    openSet.append(nnode)
            totale = time.time()
            print('shit time: ' + str(totaltime))
            print('total time: ' + str((totale - totals)))
            if endnode:
                path.append(endnode.pos())
                next = get_node(endnode.parent, closedSet)
                while next:
                    path.append(next.pos())
                    next = get_node(next.parent, closedSet)
                path = list(reversed(path))
                self.solution = path
                print('openSet: %d, closedSet: %d' % (len(openSet), len(closedSet)))
                print('solution length: ' + str(len(path)))
                print(path)
            else:
                print('no solution found')
    '''

    #new a* run
    def run(self):
        self.setmode(0)
        movecost = .75
        for startp in self.startpoints:
            start = (startp[0], startp[1], 0, 0)
            closed = []
            open = [start,]
            g = {}
            h = {}
            p = {}
            g[start] = 0
            h[start] = self.heuristic(start)
            p[start] = None
            end = None
            while len(open) > 0:
                c = open[0]
                open = open[1:]
                closed.append(c)
                end = self.can_end(c)
                if end and self.valid_move(c, end):
                    closed.append(end)
                    p[end] = c
                    break
                moves = get_moves(c)
                for move in moves:
                    if move in closed or not self.valid_move(c, move):
                        continue
                    ng = g[c] + movecost
                    nh = self.heuristic(move)
                    if move not in open:
                        if not open:
                            open.append(move)
                        else:
                            nf = ng + nh
                            for i in range(len(open)):
                                if nf < g[open[i]] + h[open[i]]:
                                    open.insert(i, move)
                                    break
                                if i == len(open) - 1:
                                    open.append(move)
                    elif ng >= g[move]:
                        continue

                    p[move] = c
                    g[move] = ng
                    h[move] = nh

            if end:
                print('solution found')
                print('open: ' + str(len(open)))
                print('closed: ' + str(len(closed)))
                path = []
                path.append(end)
                next = p[end]
                while next:
                    path.append(next)
                    next = p[next]
                path = path[::-1]
                print(len(path))
                if not self.solution or len(path) < len(self.solution):
                    self.solution = path





    def mouse_release(self, x, y, button, modifiers):
        super().mouse_release(x, y, button, modifiers)
        if y >= 200:
            gx = x // 10
            gy = (y - 200) // 10
            if not self.selected:
                self.selected = (gx, gy)
            elif self.selected != (gx, gy):
                self.selected = (gx, gy)
            else:
                self.selected = None
        self.renderoverlay()

    def setvars(self):
        self.vertex_lists = []
        self.overlays = []
        self.selected = None
        self.heuristiclabel = None
        self.solution = None
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
        run = Button(350, 120, 40, 40, 'Run', self.run)
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
                    points = [ px, py, 0, px + 10, py, 0, px + 10, py + 10, 0, px, py + 10, 0 ]
                    for point in points:
                        quads.append(point)
                    rgb = pallet[self.grid[x][y].type]
                    for i in range(4):
                        for color in rgb:
                            colors.append(color)

            self.vertex_lists.append(self._batch.add(len(quads) * 2 // 6, GL_QUADS, None, ('v3f', quads), ('c3B', colors)))
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
                        rgb = [240 - 10 * self.distgrid[x][y], 240 - 10 * self.distgrid[x][y], 240 - 10 * self.distgrid[x][y]]
                    for i in range(4):
                        for color in rgb:
                            colors.append(color)

            self.vertex_lists.append(self._batch.add(len(quads) // 2, GL_QUADS, None, ('v2f', quads), ('c3B', colors)))

    def on_draw(self):
        super().on_draw()
        if self.heuristiclabel:
            self.heuristiclabel.draw()

    def renderoverlay(self):
        for vlist in self.overlays:
            vlist.delete()
            self.overlays.remove(vlist)
        if self.solution:
            points = []
            colors = []
            for point in self.solution:
                px = (point[0] + self.offsx) * 10 + 5
                py = (point[1] + self.offsy) * 10 + 205
                points.extend((px, py, -1))
                colors.extend((240, 240, 0))
            self.overlays.append(self._batch.add(len(self.solution), GL_LINE_STRIP, None, ('v3f', points), ('c3B', colors)))
        '''
        if self.heuristiclabel:
            self.heuristiclabel.delete()
        if self.selected:
            px, py = self.selected
            self.overlays.append(self.batch.add(4, GL_LINE_LOOP, None, ('v3f', (px * 10, py * 10 + 200, -1, px * 10 + 10, py * 10 + 200, -1, px * 10 + 10, py * 10 + 210, -1, px * 10, py * 10 + 210, -1)), ('c3B', (0, 0, 240, 0, 0, 240, 0, 0, 240, 0, 0, 240))))
            text = 'None'
            gx = px + self.offsx
            gy = py + self.offsy
            if self.in_grid((gx, gy)):
                if self.grid[gx][gy].heuristic.values():
                    text = str(min(self.grid[gx][gy].heuristic.values()))
            self.heuristiclabel = pyglet.text.Label(text, font_name='Verdana', font_size=8, x=400, y=120)
        '''


window = Race(width=600, height=800, caption='Race', resizable=True)
glClearColor(0, 0, 0, 1)
pyglet.app.run()
