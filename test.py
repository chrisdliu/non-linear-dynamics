from tkg import *
import timeit

class TestViewer(Viewer):
    def draw(self):
        setup = '''
import tkinter as tk
master = tk.Tk()
canvas = tk.Canvas(master)
canvas.pack()
'''
        print(timeit.timeit(setup=setup, stmt='canvas.create_rectangle(10, 10, 10, 10, fill="white", outline="")', number=600*600))
        print('done')


app = Window(title='Viewer', size=(600, 800), frameclasses=(TestViewer,))
app.mainloop()