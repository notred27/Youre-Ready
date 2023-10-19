
# This file was generated by the Tkinter Designer by Parth Jadhav
# https://github.com/ParthJadhav/Tkinter-Designer


from pathlib import Path

# from tkinter import *
# Explicit imports to satisfy Flake8
from tkinter import *
from tkinter import ttk
import json
load_dropbox = json.loads(open("dropbox_info.json", "r").read())["Dept"]
load_dropbox.remove("")

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path("assets")


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


window = Tk()

window.geometry("696x400")
window.configure(bg = "#F2F4F1")


# Create something that merges the looks of the dropdown course menues with scrolable frames that act like comboboxes
class CustomDropDown(Frame):
    def __init__(self, parent,text,values, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)
        # parent.create_image(x,y, anchor = "nw", image= search_long_img)

        self.canvas = Canvas(self, width = 286, height = 60, bg= "#7268A6", bd=0,highlightthickness=0)
        self.canvas.create_image(2,2, anchor = "nw", image= search_long_img)
        self.entry = Entry(self,bg="#B29EC6",fg= "#f2f4f1",font=("IstokWeb Bold", 20 * -1),bd=0, )
        self.entry.place(in_=self.canvas, x=12, y = 11)

        self.text = text
        self.entry.insert(0, self.text)

        self.values = values

        # # self.canvas.create_text(12.0,11.0,anchor="nw",text = "Semester (REQUIRED):",fill="#F2F4F1",font=("IstokWeb Bold", 20 * -1))
        # self.scroll = Scrollbar(self,orient="vertical", command=self.canvas.yview)
        # self.scroll.grid(row=1, column=4, sticky='ns')

        # for i in range(3):
        #     b = Label(self.scroll, text=str(i))
        #     b.pack()
        # self.scroll.pack()

        # # self.scroll.place(in_= canvas, x=50,y=50)
        self.scroll_frame = Frame(self)
        self.scroll_frame.pack_forget()
        scrollbar = Scrollbar(self.scroll_frame)
        scrollbar.pack( side = RIGHT, fill=Y )

        self.list = Listbox(self.scroll_frame,width = 44, yscrollcommand = scrollbar.set, borderwidth=0, highlightthickness=0,selectmode=SINGLE)  #TODO: adaptive height when less than num elements?
        # for line in range(100):
        #     # self.list.insert(END, "This is line number " + str(line))
        #     self.values.append( "This is line number " + str(line))
        # # print(self.values)
        self.list.pack( side = LEFT,anchor="s", fill = BOTH )
        scrollbar.config( command = self.list.yview )

        self.canvas.pack(anchor="n",side=TOP)
        # self.scroll_frame.pack(side=BOTTOM)


        self.entry.bind('<Button-1>', self.clear_text)
        self.entry.bind('<KeyRelease>', self.manage_input)

        self.list.bind('<Button-1>', self.select)

    def clear_text(self, event):
        if self.entry.get() == self.text:
            self.entry.delete(0,len(self.text)+ 1)

            for i in range(len(self.values)):
                self.list.insert(self.list.size(), self.values[i])
        self.scroll_frame.pack(side=BOTTOM)



    def manage_input(self, event):
        value = self.entry.get()
        self.list.delete(0, self.list.size())

        if value == '':
            for i in range(len(self.values)):
                self.list.insert(self.list.size(), self.values[i])
            self.list.config(height= 11)

        else:   #TODO try to condense following lines
            
            data = []
            for item in self.values:
                if value.lower() in item.lower():
                    data.append(item)
            data.sort()
            for i in range(len(data)):
                self.list.insert(self.list.size(), data[i])
            
            if len(data) < 11:
                self.list.config(height= len(data))
            else:
                self.list.config(height= 11)


    def toggle_drop(self, event):
        print("toggle drop clicked")
        self.scroll_frame.forget()

    def select(self, event):
        try:
            self.entry.delete(0,len(self.entry.get()))
            self.entry.insert(0, self.list.selection_get())
            self.list.selection_clear(0, len(self.values))
            self.scroll_frame.forget()
        except:
            pass
       


        # self.canvas.config(height=140 )

        


class CustomCombobox(ttk.Combobox):
    def __init__(self, parent,values = None, startingText = '',fg = 'black',  *args, **kw):
        ttk.Combobox.__init__(self, parent, *args, **kw)
        # Label.__init__(self, parent, image=search_long_img)

        
        
        self.values = values
        self['values'] = values

        self.startingText = startingText
        self.set(startingText)
        self.configure(foreground="#777777")

        self.fg = fg

        self.bind('<Button-1>', self.manage_initial_text)
        self.bind('<KeyRelease>', self.manage_combobox)

    def manage_initial_text(self, event):

        if self.get() == self.startingText:
            self.set('')
            self.configure(foreground=self.fg)


    def manage_combobox(self, event):
        value = event.widget.get()

        if value == '':
            self['values'] = self.values

        else:
            data = []
            for item in self.values:
                if value.lower() in item.lower():
                    data.append(item)
            data.sort()
            self['values'] = data

    def reset(self):
        self.set(self.startingText)
        self.configure(foreground="#777777")
        self['values'] = self.values




canvas = Canvas(
    window,
    bg = "#F2F4F1",
    height = 400,
    width = 696,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)


bg_img = PhotoImage(file=relative_to_assets("search_bg.png"))
search_btn_img = PhotoImage(file=relative_to_assets("search_btn.png"))
search_long_img = PhotoImage(file=relative_to_assets("search_long.png"))
search_short_img = PhotoImage(file=relative_to_assets("search_small.png"))




canvas.create_image(102,59, anchor = "nw", image= bg_img)



search_btn = Button(image=search_btn_img,borderwidth=0,highlightthickness=0,command=lambda: print("search btn clicked"),relief="flat")
search_btn.place(x=447.0,y=234.0,width=103.0,height=60.0)

# 1st long bar
canvas.create_image(123,85, anchor = "nw", image= search_long_img)

# 2nd long bar
canvas.create_image(123,161, anchor = "nw", image= search_long_img)

# 3rd long bar
canvas.create_image(123,237, anchor = "nw", image= search_long_img)

# 1st short bar
canvas.create_image(429,85, anchor = "nw", image= search_short_img)

# 2nd short bar
canvas.create_image(429,161, anchor = "nw", image= search_short_img)

check_btn = Checkbutton(window,bd=0,highlightthickness=0, background="#7268A6", activebackground="#7268A6")
check_btn.place(in_=canvas, x = 361,y =310)

box = CustomCombobox(window, values=load_dropbox)
box.place(in_=canvas, x=123,y=85)

box.pack()


cust = CustomDropDown(window,text = "Semester (REQUIRED):", values = load_dropbox)

cust.place(in_=canvas, x=123,y=85)

# cust.pack()

canvas.create_text(135.0,249.0,anchor="nw",text="Course Type:",fill="#F2F4F1",font=("IstokWeb Bold", 20 * -1))

canvas.create_text(439.0,173.0,anchor="nw",text="Keywords:",fill="#F2F4F1",font=("IstokWeb Bold", 20 * -1))

canvas.create_text(439.0,96.0,anchor="nw",text="Course ID:",fill="#F2F4F1",font=("IstokWeb Bold", 20 * -1))

canvas.create_text(135.0,173.0,anchor="nw",text="Subject:",fill="#F2F4F1",font=("IstokWeb Bold", 20 * -1))

canvas.create_text(135.0,96.0,anchor="nw",text="Semester (REQUIRED):",fill="#F2F4F1",font=("IstokWeb Bold", 20 * -1))

canvas.create_text(386.0,311.0,anchor="nw",text="Hide unavailable classes",fill="#FFFFFF",font=("IstokWeb Bold", 16 * -1))


canvas.pack()
# window.resizable(False, False)
window.mainloop()