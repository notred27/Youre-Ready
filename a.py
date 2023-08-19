import tkinter as tk

class RoundedButton(tk.Canvas):

    def __init__(self, master, text:str="", font = ("Times", 10),radius=25, btnforeground="#AAAAAA", btnbackground="#ffffff", command=None,width = 100, height = 100, *args, **kwargs):
        super(RoundedButton, self).__init__(master, *args, **kwargs)
        self.config(bg=self.master["bg"])
        self.config(width = width, height = height)
        self.btnbackground = btnbackground
        self.command = command

        self.radius = radius        
        
        self.rect = self.round_rectangle(0, 0, width, height, tags="button", radius=radius, fill=btnbackground)
        self.text = self.create_text(width/2,height/2, text=text, tags="button", fill=btnforeground, font= font, justify="center")

        self.tag_bind("button", "<ButtonPress>", self.border)
        self.tag_bind("button", "<ButtonRelease>", self.border)
        # self.bind("<Configure>", self.resize)
        
        text_rect = self.bbox(self.text)
        if int(self["width"]) < text_rect[2]-text_rect[0]:
            self["width"] = (text_rect[2]-text_rect[0]) + 10
        
        if int(self["height"]) < text_rect[3]-text_rect[1]:
            self["height"] = (text_rect[3]-text_rect[1]) + 10
          
    def round_rectangle(self, x1, y1, x2, y2, radius=25, update=False, **kwargs): # if update is False a new rounded rectangle's id will be returned else updates existing rounded rect.
        # source: https://stackoverflow.com/a/44100075/15993687
        points = [x1+radius, y1,
                x1+radius, y1,
                x2-radius, y1,
                x2-radius, y1,
                x2, y1,
                x2, y1+radius,
                x2, y1+radius,
                x2, y2-radius,
                x2, y2-radius,
                x2, y2,
                x2-radius, y2,
                x2-radius, y2,
                x1+radius, y2,
                x1+radius, y2,
                x1, y2,
                x1, y2-radius,
                x1, y2-radius,
                x1, y1+radius,
                x1, y1+radius,
                x1, y1]

        if not update:
            return self.create_polygon(points, **kwargs, smooth=True)
        
        else:
            self.coords(self.rect, points)



    def border(self, event):
        if event.type == "4":
            self.itemconfig(self.rect, fill="#d2d6d3")
            if self.command is not None:
                self.command()

        else:
            self.itemconfig(self.rect, fill=self.btnbackground)

def func():
    print("Button pressed")

root = tk.Tk()

f= tk.Frame(root, width = 60, height = 100)
btn = RoundedButton(f, text="Info", width=60, height = 30, radius=30, btnbackground="#0078ff", btnforeground="#ffffff", command=func)
f.pack()
btn.pack()
root.mainloop()