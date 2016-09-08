import tkinter as tk
from tkinter import ttk

FONT = ('Verdana', 12)


def log(message):
    print(message)


class Page(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.load()

    def load(self):
        pass


class Viewer(Page):
    def load(self):
        self.canvas = tk.Canvas(self, width=600, height=600)
        self.canvas.pack()
        self.canvas.create_rectangle(0, 0, 600, 600, fill='white')

        upb = tk.Button(self, text='Up', width=4, height=2, command=lambda: self.up())
        upb.place(x=100, y=650)
        downb = tk.Button(self, text='Down', width=4, height=2, command=lambda: self.down())
        downb.place(x=100, y=690)
        leftb = tk.Button(self, text='Left', width=4, height=2, command=lambda: self.left())
        leftb.place(x=60, y=670)
        leftb = tk.Button(self, text='Right', width=4, height=2, command=lambda: self.right())
        leftb.place(x=140, y=670)

        z1 = tk.Button(self, text='Zoom In', width=6, height=2, command=lambda: self.zoom_in())
        z1.place(x=200, y=650)
        z2 = tk.Button(self, text='Zoom Out', width=6, height=2, command=lambda: self.zoom_out())
        z2.place(x=280, y=650)

        self.setvars()
        self.draw()

    #will override
    def setvars(self):
        pass

    def draw(self):
        self.canvas.create_rectangle(0, 0, 600, 600, fill='white')

    def up(self):
        log('Up')

    def down(self):
        log('Down')

    def left(self):
        log('Left')

    def right(self):
        log('Right')

    def zoom_in(self):
        pass

    def zoom_out(self):
        pass


class TempPage(Page):
    def load(self):
        label = tk.Label(self, text='Temp Page', font=FONT)
        label.pack(pady=10, padx=10)


class Window(tk.Tk):
    def __init__(self, title='Title', size=(600,600), frameclasses=(TempPage,), *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.wm_title(title)
        self.wm_geometry('{}x{}'.format(size[0], size[1]))

        container = tk.Frame(self)
        container.pack(side='top', fill='both', expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in frameclasses:
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='nsew')
        self.show_frame(frameclasses[0])

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()