from tkg import *


def log(message):
    print(message)


class Viewer(Page):
    def load(self):
        self.canvas = tk.Canvas(self, width=600, height=600)
        self.canvas.pack()
        self.canvas.create_rectangle(0, 0, 600, 600, fill='white')

        upb = tk.Button(self, text='Up', width=4, height=2, command=lambda: log('Up'))
        upb.place(x=100, y=650)
        downb = tk.Button(self, text='Down', width=4, height=2, command=lambda: log('Down'))
        downb.place(x=100, y=690)
        leftb = tk.Button(self, text='Left', width=4, height=2, command=lambda: log('Left'))
        leftb.place(x=60, y=670)
        leftb = tk.Button(self, text='Right', width=4, height=2, command=lambda: log('Right'))
        leftb.place(x=140, y=670)

app = Window(title='Viewer', size=(600, 800), frameclasses=(Viewer,))
app.mainloop()
