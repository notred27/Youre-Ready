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
    def __init__(self, parent,text,img, width,text_width, values,list_width=44, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)
        self.text = text
        self.values = values

        # Create canvas and entry box
        self.canvas = Canvas(self, width = width, height = 60, bg= "#7268A6", bd=0,highlightthickness=0)
        self.canvas.create_image(2,2, anchor = "nw", image= img)
        self.entry = Entry(self,bg="#B29EC6",fg= "#f2f4f1",font=("IstokWeb Bold", 20 * -1),bd=0, width = text_width)
        self.entry.place(in_=self.canvas, x=5, y = 27, anchor="w")
        self.entry.insert(0, self.text)

        
        # Create frame and scroll bar for options
        self.scroll_frame = Frame(self)
        self.scroll_frame.pack_forget()
        scrollbar = Scrollbar(self.scroll_frame)
        scrollbar.pack( side = RIGHT, fill=Y )

        self.list = Listbox(self.scroll_frame,width = list_width, yscrollcommand = scrollbar.set, borderwidth=0, highlightthickness=0,selectmode=SINGLE)  
        self.list.pack( side = LEFT,anchor="s", fill = BOTH )
    
        scrollbar.config(command = self.list.yview)
        self.canvas.pack(anchor="n",side=TOP)


        # Bind events
        self.entry.bind('<Button-1>', self.clear_text)
        self.entry.bind('<KeyRelease>', self.manage_input)
        self.list.bind('<Button-1>', self.select_option)


    def clear_text(self, event):
        # Used to clear the starting text in th entry and toggle the drop down list
        if self.entry.get() == self.text:
            self.entry.delete(0,len(self.text)+ 1)

            for i in range(len(self.values)):
                self.list.insert(self.list.size(), self.values[i])
        self.scroll_frame.pack(side=BOTTOM)


    def manage_input(self, event):
        # Used to change what is shown in hte drop down list
        self.list.config(height= 11)
        value = self.entry.get()
        self.list.delete(0, self.list.size())

        if value == '':
            for i in range(len(self.values)):
                self.list.insert(self.list.size(), self.values[i])
            

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
            


    def select_option(self, event):
        # Used to select a value from the drop down list
        try:    #FIXME edge case when first selescting a value
            if self.entry.get() != self.list.selection_get():
                self.entry.delete(0,len(self.entry.get()))
                self.entry.insert(0, self.list.selection_get())
                self.list.selection_clear(0, len(self.values))
                self.scroll_frame.forget()
        except:
            pass
       


#Photo images for search widget
bg_img = PhotoImage(file=relative_to_assets("search_bg.png"))
search_btn_img = PhotoImage(file=relative_to_assets("search_btn.png"))
search_long_img = PhotoImage(file=relative_to_assets("search_long.png"))
search_short_img = PhotoImage(file=relative_to_assets("search_small.png"))


canvas = Canvas(window,bg = "#F2F4F1",height = 400,width = 696,bd = 0,highlightthickness = 0,relief = "ridge")
canvas.create_image(102,59, anchor = "nw", image= bg_img)


# Search button for submitting form
search_btn = Button(image=search_btn_img,borderwidth=0,highlightthickness=0,command=lambda: print("search btn clicked"),relief="flat")
search_btn.place(in_=canvas, x=447.0,y=234.0,width=103.0,height=60.0)

# 1st long bar
# canvas.create_image(123,85, anchor = "nw", image= search_long_img)

semester_box = CustomDropDown(window,text = "Semester (REQUIRED):", values = load_dropbox, width = 286, img = search_long_img, text_width = 25)
semester_box.place(in_=canvas, x=123,y=85)


# 2nd long bar
# canvas.create_image(123,161, anchor = "nw", image= search_long_img)

subject_box = CustomDropDown(window,text = "Subject:", values = load_dropbox, width = 286, img = search_long_img, text_width = 25)
subject_box.place(in_=canvas, x=123,y=161)

# 3rd long bar
# canvas.create_image(123,237, anchor = "nw", image= search_long_img)

course_box = CustomDropDown(window,text = "Course Type:", values = load_dropbox, width = 286, img = search_long_img, text_width = 25)
course_box.place(in_=canvas, x=123,y=237)




# 1st short bar
# canvas.create_image(429,85, anchor = "nw", image= search_short_img)
id_box = CustomDropDown(window,text = "Course ID:", values = load_dropbox, width = 146, img = search_short_img, text_width = 12, list_width=21)
id_box.place(in_=canvas, x=429,y=85)

# 2nd short bar
canvas.create_image(429,161, anchor = "nw", image= search_short_img)
keywords_box = CustomDropDown(window,text = "Keywords:", values = load_dropbox, width = 146, img = search_short_img, text_width = 12, list_width=21)
keywords_box.place(in_=canvas, x=429,y=161)

# Checkbutton for hiding unavailable classes
check_btn = Checkbutton(window,bd=0,highlightthickness=0, background="#7268A6", activebackground="#7268A6")
check_btn.place(in_=canvas, x = 361,y =310)
canvas.create_text(386.0,311.0,anchor="nw",text="Hide unavailable classes",fill="#FFFFFF",font=("IstokWeb Bold", 16 * -1))




#Keep lift order so widgets don't obscure each other
semester_box.lift(aboveThis=subject_box)
semester_box.lift(aboveThis=course_box)
subject_box.lift(aboveThis=course_box)
semester_box.lift(aboveThis=check_btn)
subject_box.lift(aboveThis=check_btn)
course_box.lift(aboveThis=check_btn)
id_box.lift(aboveThis=keywords_box)





canvas.pack()
# window.resizable(False, False)
window.mainloop()
