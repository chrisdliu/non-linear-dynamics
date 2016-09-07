import tkinter as tk
from tkinter import ttk

FONT = ('Verdana', 12)


class Page(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.load()

    def load(self):
        pass


class TestPage(Page):
    def load(self):
        label = tk.Label(self, text='Test Page', font=FONT)
        label.pack(pady=10, padx=10)


class Window(tk.Tk):
    def __init__(self, title='Title', size=(600,600), frameclasses=(TestPage,), *args, **kwargs):
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
